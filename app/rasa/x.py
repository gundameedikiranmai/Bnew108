import yaml

question = [
    {
        "text": "What is your current work status? (Working or in between Jobs)"
    },
    {
        "text": "What is your visa status?",
        "buttons": [
            {
                "title": "US Citizen",
                "payload": "US Citizen",
            },
            {
                "title": "Green Card",
                "payload": "Green Card",
            },
            {
                "title": "H1B Visa",
                "payload": "H1B Visa",
            },
            {
                "title": "TN permit",
                "payload": "TN permit",
            },
            {
                "title": "OPT/CPT visa",
                "payload": "OPT/CPT visa",
            }
        ]
    }
]

# print(yaml.dump({"common_questions": question}))
print(yaml.dump({"common_questions": ["1"]}))