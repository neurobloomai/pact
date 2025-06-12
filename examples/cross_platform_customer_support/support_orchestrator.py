#!/usr/bin/env python3
"""
PACT Cross-Platform Customer Support - Core Orchestrator

This module provides the main support coordination logic, managing tickets
across multiple communication channels through specialized PACT agents.
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict, field
from enum import Enum
import structlog
from prometheus_client import Counter, Histogram, Gauge
import redis.asyncio as redis

# Configure structured logging
logger = structlog.get_logger(__name__)

# Prometheus metrics
SUPPORT_TICKETS_TOTAL = Counter('pact_support_tickets_total', 'Total support tickets', ['channel', 'priority', 'status'])
TICKET_RESOLUTION_TIME = Histogram('pact_ticket_resolution_seconds', 'Ticket resolution time', ['channel', 'priority'])
ACTIVE_TICKETS = Gauge('pact_active_tickets', 'Currently active tickets')
CUSTOMER_SATISFACTION = Histogram('pact_customer_satisfaction_score', 'Customer satisfaction scores', ['channel'])
AGENT_ACTIONS = Counter('pact_support_agent_actions_total', 'Support agent actions', ['agent', 'action', 'status'])


class SupportChannel(Enum):
    """Supported communication channels"""
    EMAIL = "email"
    SLACK = "slack" 
    WHATSAPP = "whatsapp"
    CHAT_WIDGET = "chat_widget"
    PHONE = "phone"
    TWITTER = "twitter"
    FACEBOOK = "facebook"
    DISCORD = "discord"
    TELEGRAM = "telegram"
    SMS = "sms"
    ZENDESK = "zendesk"
    FRESHDESK = "freshdesk"


class Priority(Enum):
    """Ticket priority levels"""
    LOW = "low"
    MEDIUM = "medium" 
    HIGH = "high"
    URGENT = "urgent"
    CRITICAL = "critical"


class TicketStatus(Enum):
    """Ticket lifecycle status"""
    NEW = "new"
    TRIAGED = "triaged"
    IN_PROGRESS = "in_progress"
    WAITING_CUSTOMER = "waiting_customer"
    WAITING_INTERNAL = "waiting_internal"
    ESCALATED = "escalated"
    RESOLVED = "resolved"
    CLOSED = "closed"
    REOPENED = "reopened"


class InteractionType(Enum):
    """Types of support interactions"""
    CUSTOMER_MESSAGE = "customer_message"
    AGENT_RESPONSE = "agent_response"
    SYSTEM_ACTION = "system_action"
    AUTO_RESPONSE = "auto_response"
    ESCALATION = "escalation"
    RESOLUTION = "resolution"


@dataclass
class SupportTicket:
    """Unified support ticket across all channels"""
    ticket_id: str
    customer_id: str
    channel: SupportChannel
    priority: Priority
    status: TicketStatus
    subject: str
    description: str
    created_at: datetime
    updated_at: datetime
    assigned_agent: Optional[str] = None
    escalated_to: Optional[str] = None
    resolution_time_minutes: Optional[int] = None
    satisfaction_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    attachments: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        result['channel'] = self.channel.value
        result['priority'] = self.priority.value
        result['status'] = self.status.value
        result['created_at'] = self.created_at.isoformat()
        result['updated_at'] = self.updated_at.isoformat()
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SupportTicket':
        """Create from dictionary"""
        data['channel'] = SupportChannel(data['channel'])
        data['priority'] = Priority(data['priority'])
        data['status'] = TicketStatus(data['status'])
        data['created_at'] = datetime.fromisoformat(data['created_at'])
        data['updated_at'] = datetime.fromisoformat(data['updated_at'])
        return cls(**data)


@dataclass
class CustomerProfile:
    """Unified customer profile across all interactions"""
    customer_id: str
    name: str
    email: str
    phone: Optional[str] = None
    preferred_channel: Optional[SupportChannel] = None
    preferred_language: str = "en"
    timezone: str = "UTC"
    vip_status: bool = False
    lifetime_value: float = 0.0
    satisfaction_history: List[float] = field(default_factory=list)
    interaction_count: int = 0
    last_interaction: Optional[datetime] = None
    open_tickets: int = 0
    resolved_tickets: int = 0
    escalation_history: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    custom_fields: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        result = asdict(self)
        if self.preferred_channel:
            result['preferred_channel'] = self.preferred_channel.value
        if self.last_interaction:
            result['last_interaction'] = self.last_interaction.isoformat()
        return result


@dataclass
class SupportInteraction:
    """Individual support interaction record"""
    interaction_id: str
    ticket_id: str
    agent_id: Optional[str]
    customer_id: str
    channel: SupportChannel
    interaction_type: InteractionType
    content: str
    timestamp: datetime
    sentiment_score: Optional[float] = None
    resolution_offered: bool = False
    escalation_triggered: bool = False
    attachments: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeArticle:
    """Knowledge base article"""
    article_id: str
    title: str
    content: str
    category: str
    tags: List[str]
    created_at: datetime
    updated_at: datetime
    author: str
    view_count: int = 0
    helpful_votes: int = 0
    unhelpful_votes: int = 0
    confidence_score: float = 0.0
    related_articles: List[str] = field(default_factory=list)


class SupportAgent:
    """Abstract base class for PACT support agents"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = structlog.get_logger(__name__, agent=name)
    
    async def execute_pact_action(self, action: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a PACT action - to be implemented by specific agents"""
        raise NotImplementedError("Support agents must implement execute_pact_action")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check agent health status"""
        return {
            "agent": self.name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat()
        }


class PACTSupportOrchestrator:
    """Main PACT support coordination engine"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379"):
        self.agents: Dict[str, SupportAgent] = {}
        self.redis_client = redis.from_url(redis_url)
        self.active_tickets: Dict[str, SupportTicket] = {}
        self.customer_profiles: Dict[str, CustomerProfile] = {}
        self.knowledge_base: Dict[str, KnowledgeArticle] = {}
        self.escalation_rules: Dict[str, Any] = {}
        self.auto_response_templates: Dict[str, str] = {}
        self.logger = structlog.get_logger(__name__)
        
        # Default escalation rules
        self.escalation_rules = {
            "vip_customer": {"auto_escalate": True, "max_wait_minutes": 5},
            "critical_priority": {"auto_escalate": True, "max_wait_minutes": 10},
            "negative_sentiment": {"threshold": 0.3, "auto_escalate": True},
            "multiple_interactions": {"threshold": 3, "auto_escalate": True}
        }
    
    async def initialize(self):
        """Initialize the support orchestrator"""
        await self.redis_client.ping()
        self.logger.info("Support orchestrator initialized")
    
    async def shutdown(self):
        """Gracefully shutdown the orchestrator"""
        # Close active tickets gracefully
        for ticket_id in list(self.active_tickets.keys()):
            await self._save_ticket_state(self.active_tickets[ticket_id])
        
        await self.redis_client.close()
        self.logger.info("Support orchestrator shutdown complete")
    
    def register_agent(self, agent: SupportAgent):
        """Register a PACT support agent"""
        self.agents[agent.name] = agent
        self.logger.info("Support agent registered", agent=agent.name)
    
    def register_escalation_rule(self, rule_name: str, rule_config: Dict[str, Any]):
        """Register custom escalation rule"""
        self.escalation_rules[rule_name] = rule_config
        self.logger.info("Escalation rule registered", rule=rule_name)
    
    async def handle_customer_contact(self, contact_data: Dict[str, Any]) -> str:
        """Main entry point for customer support requests"""
        
        try:
            # Create or update ticket
            ticket = await self._create_or_update_ticket(contact_data)
            
            # Record interaction
            interaction = await self._record_interaction(ticket, contact_data)
            
            # Execute support workflow
            await self._execute_support_workflow(ticket, interaction)
            
            # Update metrics
            SUPPORT_TICKETS_TOTAL.labels(
                channel=ticket.channel.value,
                priority=ticket.priority.value,
                status=ticket.status.value
            ).inc()
            
            return ticket.ticket_id
            
        except Exception as e:
            self.logger.error("Failed to handle customer contact", error=str(e))
            # Create emergency ticket for manual handling
            emergency_ticket = await self._create_emergency_ticket(contact_data, str(e))
            return emergency_ticket.ticket_id
    
    async def _create_or_update_ticket(self, contact_data: Dict[str, Any]) -> SupportTicket:
        """Create new ticket or update existing one"""
        
        customer_id = contact_data.get("customer_id")
        channel = SupportChannel(contact_data.get("channel"))
        
        # Check for existing open tickets from this customer in the same channel
        existing_ticket = await self._find_existing_ticket(customer_id, channel)
        
        if existing_ticket and existing_ticket.status not in [TicketStatus.RESOLVED, TicketStatus.CLOSED]:
            # Update existing ticket
            existing_ticket.updated_at = datetime.now()
            existing_ticket.description += f"\n\n--- Follow-up Message ({datetime.now().strftime('%Y-%m-%d %H:%M')}) ---\n{contact_data.get('message', '')}"
            
            # Check if this is a reopening
            if existing_ticket.status == TicketStatus.RESOLVED:
                existing_ticket.status = TicketStatus.REOPENED
                existing_ticket.resolution_time_minutes = None
            
            await self._save_ticket_state(existing_ticket)
            return existing_ticket
        else:
            # Create new ticket
            ticket = SupportTicket(
                ticket_id=self._generate_ticket_id(),
                customer_id=customer_id,
                channel=channel,
                priority=Priority.MEDIUM,  # Will be updated by triage
                status=TicketStatus.NEW,
                subject=contact_data.get("subject", "Support Request"),
                description=contact_data.get("message", ""),
                created_at=datetime.now(),
                updated_at=datetime.now(),
                tags=[],
                metadata=contact_data.get("metadata", {}),
                attachments=contact_data.get("attachments", [])
            )
            
            self.active_tickets[ticket.ticket_id] = ticket
            await self._save_ticket_state(ticket)
            ACTIVE_TICKETS.inc()
            
            return ticket
    
    async def _record_interaction(self, ticket: SupportTicket, contact_data: Dict[str, Any]) -> SupportInteraction:
        """Record the customer interaction"""
        
        interaction = SupportInteraction(
            interaction_id=f"INT_{uuid.uuid4().hex[:8].upper()}",
            ticket_id=ticket.ticket_id,
            agent_id=None,  # Customer initiated
            customer_id=ticket.customer_id,
            channel=ticket.channel,
            interaction_type=InteractionType.CUSTOMER_MESSAGE,
            content=contact_data.get("message", ""),
            timestamp=datetime.now(),
            attachments=contact_data.get("attachments", []),
            metadata=contact_data.get("metadata", {})
        )
        
        # Store interaction
        await self.redis_client.lpush(
            f"interactions:{ticket.ticket_id}",
            json.dumps(asdict(interaction), default=str)
        )
        
        return interaction
    
    async def _execute_support_workflow(self, ticket: SupportTicket, interaction: SupportInteraction):
        """Execute the complete support workflow"""
        
        workflow_start = datetime.now()
        
        try:
            # Stage 1: Channel Processing
            await self._process_channel_message(ticket, interaction)
            
            # Stage 2: Customer Context Enrichment
            await self._enrich_customer_context(ticket)
            
            # Stage 3: Intelligent Triage
            await self._perform_triage(ticket, interaction)
            
            # Stage 4: Knowledge Search & Auto-Resolution Attempt
            await self._attempt_auto_resolution(ticket, interaction)
            
            # Stage 5: Route to Human Agent (if needed)
            if ticket.status not in [TicketStatus.RESOLVED, TicketStatus.WAITING_CUSTOMER]:
                await self._route_to_human_agent(ticket)
            
            # Stage 6: Check Escalation Rules
            await self._check_escalation_rules(ticket, interaction)
            
            # Stage 7: Analytics & Learning
            await self._track_analytics(ticket, interaction)
            
            # Update ticket state
            await self._save_ticket_state(ticket)
            
            workflow_duration = (datetime.now() - workflow_start).total_seconds()
            self.logger.info(
                "Support workflow completed",
                ticket_id=ticket.ticket_id,
                duration_seconds=workflow_duration,
                final_status=ticket.status.value
            )
            
        except Exception as e:
            self.logger.error("Support workflow failed", ticket_id=ticket.ticket_id, error=str(e))
            await self._handle_workflow_failure(ticket, str(e))
    
    async def _process_channel_message(self, ticket: SupportTicket, interaction: SupportInteraction):
        """Process message through channel-specific agent"""
        
        if "channel" not in self.agents:
            return
        
        channel_agent = self.agents["channel"]
        
        try:
            result = await channel_agent.execute_pact_action("channel.receive_message", {
                "ticket_id": ticket.ticket_id,
                "channel": ticket.channel.value,
                "message": interaction.content,
                "customer_id": ticket.customer_id,
                "attachments": interaction.attachments,
                "metadata": interaction.metadata
            })
            
            if result.get("success"):
                # Update ticket with processed message data
                processed_data = result.get("processed_message", {})
                ticket.metadata.update(processed_data)
                
                # Update interaction with sentiment
                if "sentiment_score" in processed_data:
                    interaction.sentiment_score = processed_data["sentiment_score"]
                
                # Detect urgency indicators
                if processed_data.get("urgency_detected"):
                    ticket.priority = Priority.HIGH
                    ticket.tags.append("urgent")
                
                AGENT_ACTIONS.labels(agent="channel", action="receive_message", status="success").inc()
            else:
                AGENT_ACTIONS.labels(agent="channel", action="receive_message", status="failed").inc()
                
        except Exception as e:
            self.logger.error("Channel processing failed", ticket_id=ticket.ticket_id, error
