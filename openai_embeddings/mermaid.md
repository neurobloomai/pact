flowchart TD

    Start[Start: User Input] --> Preprocess[Preprocess: Normalize Text]

    subgraph Embedding Model
        direction TB
        choice{Use OpenAI?}
        choice -->|Yes| OpenAIModel[OpenAI API\n(text-embedding-3-small)]
        choice -->|No| STModel[SentenceTransformer\n(all-MiniLM-L6-v2)]
    end

    Preprocess --> choice

    OpenAIModel --> InputVec1[Get Embedding Vector]
    STModel --> InputVec2[Get Embedding Vector]

    InputVec1 --> Match
    InputVec2 --> Match

    subgraph Matcher
        Match[Cosine Similarity\nwith Known Intents]
        Match --> ThresholdCheck{Similarity ≥ Threshold?}
        ThresholdCheck -->|Yes| MatchIntent[Return Best Match Intent]
        ThresholdCheck -->|No| UnknownIntent[Return "unknown_intent"]
    end

    MatchIntent --> End[End]
    UnknownIntent --> End
