import json
import random
import uuid

# Configuration
NUM_RECORDS = 1000 # Let's start with 1,000 to test the waters
OUTPUT_FILE = 'large_claims_data.json'

# Seed data for generation
policy_types = ["Commercial Property", "General Liability", "Commercial Auto", "Professional Liability"]
jurisdictions = ["TX", "CA", "FL", "IL", "GA", "NY", "MA", "OH", "PA", "AZ", "WA", "MN", "NJ"]
outcomes = ["Settled", "Open", "Litigated"]

# Procedural text components
scenarios = {
    "Commercial Property": [
        {"loss": "Water Damage", "desc": "Pipe burst in {location} causing damage to {items}. {context}.", "factors": ["water damage", "plumbing", "property loss"]},
        {"loss": "Fire", "desc": "Electrical fire originated in {location}. Destroyed {items}. {context}.", "factors": ["fire", "electrical", "total loss"]},
        {"loss": "Theft", "desc": "Break-in at {location}. Missing {items}. {context}.", "factors": ["security breach", "stolen inventory"]}
    ],
    "General Liability": [
        {"loss": "Slip and Fall", "desc": "Individual slipped at {location}. Sustained injuries requiring {items}. {context}.", "factors": ["bodily injury", "premises liability"]},
        {"loss": "Product Liability", "desc": "Defective product caused harm at {location}. Claim involves {items}. {context}.", "factors": ["manufacturing defect", "injury"]}
    ],
    "Commercial Auto": [
        {"loss": "Collision", "desc": "Company vehicle collided with {location}. Damage to {items}. {context}.", "factors": ["traffic accident", "vehicle damage"]}
    ],
    "Professional Liability": [
        {"loss": "Errors & Omissions", "desc": "Failure to deliver services at {location} resulting in loss of {items}. {context}.", "factors": ["negligence", "financial loss"]}
    ]
}

locations = ["retail storefront", "corporate office", "manufacturing warehouse", "client site", "parking facility", "server room"]
items = ["electronic inventory", "drywall and flooring", "heavy machinery", "medical care", "third-party property", "revenue"]
contexts = ["Disputed liability between parties", "Clear video evidence available", "Weather conditions cited as factor", "Maintenance logs missing", "Routine operations at time of incident"]

def generate_claim(index):
    policy = random.choice(policy_types)
    scenario = random.choice(scenarios[policy])
    outcome = random.choice(outcomes)
    
    amount = random.randint(5000, 500000)
    
    description = scenario["desc"].format(
        location=random.choice(locations),
        items=random.choice(items),
        context=random.choice(contexts)
    )
    
    claim = {
        "id": f"SYN-{1000 + index}",
        "policy_type": policy,
        "loss_type": scenario["loss"],
        "description": description,
        "outcome": outcome,
        "jurisdiction": random.choice(jurisdictions),
        "key_factors": scenario["factors"] + [random.choice(["high severity", "low severity", "complex investigation"])]
    }
    
    if outcome == "Open":
        claim["reserve_amount"] = amount
        claim["settlement_amount"] = None
        claim["days_open"] = random.randint(10, 100)
    else:
        claim["settlement_amount"] = amount
        claim["reserve_amount"] = None
        claim["days_to_resolution"] = random.randint(30, 365)
        
    return claim

print(f"Generating {NUM_RECORDS} synthetic claims...")
new_claims = [generate_claim(i) for i in range(NUM_RECORDS)]

# Wrap it in the Elysian JSON structure
output_data = {
    "metadata": {
        "description": f"Synthetic dataset of {NUM_RECORDS} claims",
        "version": "1.1"
    },
    "claims": new_claims
}

with open(OUTPUT_FILE, 'w') as f:
    json.dump(output_data, f, indent=2)

print(f"Successfully saved to {OUTPUT_FILE}")