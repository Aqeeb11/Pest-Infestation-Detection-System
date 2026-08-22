"""
Treatment and management knowledge base for the grape ML project.

IMPORTANT:
This database provides general management guidance.
Chemical treatment must always be checked against the current
product label, crop stage, PHI requirements and local agricultural
advisories before application.
"""

TREATMENT_DATABASE = {

    # ==========================================================
    # DISEASES
    # ==========================================================

    "Bacterial Rot": {
        "name": "Bacterial Rot",
        "type": "disease",
        "description": "Bacterial disease condition affecting grape tissues.",
        "symptoms": [
            "Water-soaked or deteriorating tissue",
            "Darkening of affected tissue",
            "Rotting of affected plant or berry tissue"
        ],
        "management": [
            "Remove and destroy visibly infected plant material.",
            "Maintain good vineyard sanitation.",
            "Improve canopy aeration.",
            "Avoid prolonged moisture on leaves and bunches.",
            "Monitor affected vines regularly."
        ],
        "prevention": [
            "Use healthy planting material.",
            "Maintain an open canopy.",
            "Remove damaged plant material.",
            "Avoid unnecessary handling of diseased tissue."
        ],
        "treatment_note": (
            "Use crop-stage-specific grape disease-management guidance. "
            "Do not apply antibiotics or other chemicals without current "
            "local agricultural recommendations."
        ),
        "verification_status": "grape disease; management guidance available",
    },

    "Black Measles": {
        "name": "Black Measles",
        "type": "disease",
        "description": "Common name associated with Esca-related grapevine disease.",
        "symptoms": [
            "Leaf discoloration and necrotic patterns",
            "Decline of affected vines",
            "Dark symptoms may occur on affected berries or tissues"
        ],
        "management": [
            "Remove severely affected plant material where appropriate.",
            "Maintain vineyard sanitation.",
            "Prune carefully.",
            "Disinfect pruning tools between affected and healthy vines.",
            "Monitor affected vines for further decline."
        ],
        "prevention": [
            "Use healthy planting material.",
            "Maintain good pruning practices.",
            "Sanitize pruning equipment.",
            "Remove severely affected material when appropriate."
        ],
        "treatment_note": (
            "There is no single universal curative treatment. "
            "Management depends on vine age, severity and vineyard condition."
        ),
        "verification_status": "grape disease; management-focused recommendation",
    },

    "Black Rot": {
        "name": "Black Rot",
        "type": "disease",
        "description": "Fungal disease that can affect grape leaves, shoots and berries.",
        "symptoms": [
            "Dark leaf lesions",
            "Darkening and shriveling of affected berries",
            "Mummified infected berries"
        ],
        "management": [
            "Remove infected berries and plant material.",
            "Remove mummified berries from the vineyard.",
            "Maintain good canopy airflow.",
            "Monitor developing bunches regularly.",
            "Use an appropriate grape fungicide program only according to current recommendations."
        ],
        "prevention": [
            "Remove infected and mummified berries.",
            "Maintain good canopy management.",
            "Avoid excessive canopy density.",
            "Monitor disease after wet weather."
        ],
        "treatment_note": (
            "Fungicide selection must follow current grape-specific "
            "recommendations, crop stage and product label."
        ),
        "verification_status": "grape disease; management guidance available",
    },

    "Downy Mildew": {
        "name": "Downy Mildew",
        "type": "disease",
        "description": "Important grape disease favored by wet and humid conditions.",
        "symptoms": [
            "Yellow or oil-spot-like leaf lesions",
            "White downy growth under suitable conditions",
            "Damage to young leaves and bunches"
        ],
        "management": [
            "Remove infected leaves and plant material where practical.",
            "Improve canopy aeration.",
            "Reduce excessive canopy density.",
            "Monitor weather and disease risk.",
            "Follow crop-stage-specific disease management."
        ],
        "prevention": [
            "Maintain an open canopy.",
            "Improve air circulation.",
            "Remove infected material promptly.",
            "Avoid prolonged leaf wetness.",
            "Monitor vineyards after wet weather."
        ],
        "treatment_note": (
            "ICAR-NRCG grape advisories provide crop-stage-specific "
            "management recommendations for downy mildew."
        ),
        "verification_status": "grape disease; ICAR-NRCG guidance available",
    },

    "Healthy Leaves": {
        "name": "Healthy Leaves",
        "type": "healthy",
        "description": "No disease class represented in the model was detected.",
        "symptoms": [],
        "management": [
            "No disease treatment is indicated from this prediction.",
            "Continue regular vineyard monitoring."
        ],
        "prevention": [
            "Maintain good canopy management.",
            "Maintain vineyard sanitation.",
            "Regularly inspect leaves, shoots and bunches.",
            "Monitor for early pest and disease symptoms."
        ],
        "treatment_note": (
            "Healthy leaf prediction: no disease treatment required. "
            "Continue preventive management and monitoring."
        ),
        "verification_status": "healthy class; prevention only",
    },

    "Leaf Blight": {
        "name": "Leaf Blight",
        "type": "disease",
        "description": "Leaf disease class representing blight or leaf-spot symptoms in the dataset.",
        "symptoms": [
            "Leaf spots or lesions",
            "Brown or necrotic areas",
            "Premature deterioration of affected leaves"
        ],
        "management": [
            "Remove severely infected leaves where practical.",
            "Maintain vineyard sanitation.",
            "Improve canopy ventilation.",
            "Avoid prolonged leaf wetness.",
            "Confirm the causal organism before selecting a specific chemical treatment."
        ],
        "prevention": [
            "Maintain good canopy airflow.",
            "Remove infected plant debris.",
            "Monitor leaves regularly.",
            "Avoid excessive humidity inside the canopy."
        ],
        "treatment_note": (
            "The exact causal organism represented by this dataset label "
            "should be confirmed before selecting a disease-specific chemical."
        ),
        "verification_status": "grape disease class; causal organism requires confirmation",
    },

    "Powdery Mildew": {
        "name": "Powdery Mildew",
        "type": "disease",
        "description": "Fungal disease producing powdery growth on grape tissues.",
        "symptoms": [
            "White powdery growth",
            "Affected leaves and shoots",
            "Affected berries may develop surface damage"
        ],
        "management": [
            "Maintain good canopy ventilation.",
            "Remove severely affected material where practical.",
            "Monitor new growth regularly.",
            "Use integrated disease-management practices.",
            "Follow current crop-stage-specific fungicide recommendations when required."
        ],
        "prevention": [
            "Maintain an open canopy.",
            "Monitor susceptible new growth.",
            "Use preventive integrated disease-management practices.",
            "Avoid excessive canopy density."
        ],
        "treatment_note": (
            "ICAR-NRCG has grape-specific powdery mildew management guidance "
            "including biological and fungicide-based approaches."
        ),
        "verification_status": "grape disease; ICAR-NRCG guidance available",
    },


    # ==========================================================
    # PESTS
    # ==========================================================

    "Ampelophaga": {
        "name": "Ampelophaga",
        "type": "pest",
        "description": "Grapevine-associated moth/caterpillar pest group.",
        "symptoms": [
            "Leaf feeding",
            "Defoliation",
            "Damage to young grapevine growth"
        ],
        "management": [
            "Regularly inspect leaves and young shoots.",
            "Remove and destroy visible larvae where practical.",
            "Remove infested pruning material.",
            "Use light or pheromone-based monitoring where appropriate.",
            "Use IPM-based caterpillar management when infestation is significant."
        ],
        "prevention": [
            "Remove pruning waste from the vineyard.",
            "Maintain vineyard sanitation.",
            "Monitor moth activity.",
            "Avoid unnecessary broad-spectrum insecticide use."
        ],
        "treatment_note": (
            "Use current grape caterpillar-management recommendations "
            "and approved products only when necessary."
        ),
        "verification_status": "grape-associated pest; IPM guidance available",
    },

    "Brevipalpus_lewisi": {
        "name": "Brevipalpus_lewisi",
        "type": "pest",
        "description": "Flat mite species; host associations should be confirmed before grape-specific treatment.",
        "symptoms": [
            "Mite feeding damage",
            "Discoloration or surface injury",
            "Damage may increase under favorable conditions"
        ],
        "management": [
            "Inspect leaves and plant surfaces for mites.",
            "Use a hand lens for confirmation.",
            "Avoid unnecessary broad-spectrum pesticide applications.",
            "Use an appropriate miticide only after confirming the pest."
        ],
        "prevention": [
            "Regular mite monitoring.",
            "Maintain vineyard hygiene.",
            "Protect beneficial organisms where possible."
        ],
        "treatment_note": (
            "Confirm species and crop association before applying a "
            "mite-specific treatment."
        ),
        "verification_status": "species requires field confirmation for grape treatment",
    },

    "Cicadella_viridis": {
        "name": "Cicadella_viridis",
        "type": "pest",
        "description": "Leafhopper species recorded in vineyard environments.",
        "symptoms": [
            "Sap feeding",
            "Leaf discoloration",
            "Possible reduction in plant vigor under heavy populations"
        ],
        "management": [
            "Regularly monitor foliage for leafhoppers.",
            "Manage excessive vegetation that supports pest populations.",
            "Use IPM and threshold-based intervention.",
            "Avoid unnecessary broad-spectrum insecticides."
        ],
        "prevention": [
            "Maintain vineyard sanitation.",
            "Monitor weeds and surrounding vegetation.",
            "Inspect new growth regularly."
        ],
        "treatment_note": (
            "Confirm the species and infestation level before chemical treatment."
        ),
        "verification_status": "vineyard-associated leafhopper; species-specific treatment requires confirmation",
    },

    "Colomerus_vitis": {
        "name": "Colomerus_vitis",
        "type": "pest",
        "description": "Grape erineum mite associated specifically with grapevines.",
        "symptoms": [
            "Erineum or felt-like patches on leaves",
            "Leaf distortion",
            "Bud or shoot damage in severe cases"
        ],
        "management": [
            "Monitor new growth and leaves.",
            "Identify infestations early.",
            "Remove severely affected plant material where practical.",
            "Use an appropriate grape mite-management program when required."
        ],
        "prevention": [
            "Use healthy planting material.",
            "Monitor vines during new growth.",
            "Avoid unnecessary broad-spectrum pesticide use."
        ],
        "treatment_note": (
            "Species confirmation is important because mite control depends "
            "on the type of mite and crop stage."
        ),
        "verification_status": "grape-specific pest; management guidance available",
    },

    "Erythroneura_apicalis": {
        "name": "Erythroneura_apicalis",
        "type": "pest",
        "description": "Leafhopper pest associated with grapevine foliage.",
        "symptoms": [
            "Sap-feeding injury",
            "Leaf discoloration",
            "Possible reduction in photosynthetic leaf area"
        ],
        "management": [
            "Monitor leaves for adults and nymphs.",
            "Maintain canopy management.",
            "Use threshold-based IPM.",
            "Protect natural enemies where possible."
        ],
        "prevention": [
            "Regularly inspect leaves.",
            "Maintain balanced canopy growth.",
            "Avoid unnecessary broad-spectrum insecticide applications."
        ],
        "treatment_note": (
            "Use current local recommendations after confirming the pest."
        ),
        "verification_status": "grape-associated leafhopper; field confirmation recommended",
    },

    "Lycorma_delicatula": {
        "name": "Lycorma_delicatula",
        "type": "pest",
        "description": "Spotted lanternfly, an important grapevine-feeding pest.",
        "symptoms": [
            "Sap feeding",
            "Honeydew deposition",
            "Sooty mold development",
            "Vine stress under heavy infestation"
        ],
        "management": [
            "Regularly inspect vines and surrounding host plants.",
            "Remove egg masses where practical.",
            "Use physical and mechanical control where feasible.",
            "Use integrated pest management.",
            "Follow current local regulatory and agricultural guidance."
        ],
        "prevention": [
            "Monitor vineyard borders.",
            "Inspect plant material entering the vineyard.",
            "Remove egg masses when found.",
            "Monitor populations throughout the season."
        ],
        "treatment_note": (
            "Treatment depends strongly on local regulations and pest status. "
            "Use current agricultural authority recommendations."
        ),
        "verification_status": "grape pest; IPM guidance available",
    },

    "Miridae": {
        "name": "Miridae",
        "type": "pest",
        "description": "Miridae is a large insect family; the model label does not identify one exact species.",
        "symptoms": [
            "Possible feeding injury",
            "Leaf or shoot damage depending on species"
        ],
        "management": [
            "Confirm the exact mirid species before treatment.",
            "Inspect feeding damage and insect morphology.",
            "Use IPM after species identification."
        ],
        "prevention": [
            "Regular vineyard scouting.",
            "Monitor surrounding vegetation.",
            "Avoid unnecessary broad-spectrum insecticides."
        ],
        "treatment_note": (
            "No single species-specific treatment should be attached to "
            "the family-level label 'Miridae'. Confirm the pest first."
        ),
        "verification_status": "family-level class; species confirmation required",
    },

    "Oides_decempunctata": {
        "name": "Oides_decempunctata",
        "type": "pest",
        "description": "Leaf-feeding beetle represented in the pest dataset.",
        "symptoms": [
            "Leaf feeding",
            "Leaf holes",
            "Defoliation under heavy infestation"
        ],
        "management": [
            "Regularly inspect leaves.",
            "Hand-remove beetles where practical in small infestations.",
            "Remove heavily infested plant material when appropriate.",
            "Use IPM-based beetle management for severe infestation."
        ],
        "prevention": [
            "Maintain vineyard sanitation.",
            "Monitor new growth.",
            "Remove weeds and alternate hosts where appropriate."
        ],
        "treatment_note": (
            "Confirm the species and infestation severity before chemical treatment."
        ),
        "verification_status": "pest class; grape association should be field-confirmed",
    },

    "Panonchus_citri": {
        "name": "Panonchus_citri",
        "type": "pest",
        "description": "Citrus-associated mite label present in the pest dataset.",
        "symptoms": [
            "Mite feeding injury may cause leaf discoloration"
        ],
        "management": [
            "Do not automatically apply grape-specific treatment based only on this prediction.",
            "Confirm the pest species and host crop."
        ],
        "prevention": [
            "Obtain expert identification if detected on grapevine.",
            "Monitor the affected plant carefully."
        ],
        "treatment_note": (
            "This class is not sufficiently verified as a grape-specific pest. "
            "Confirm identification before applying any treatment."
        ),
        "verification_status": "NOT VERIFIED as grape-specific",
    },

    "Papilio_xuthus": {
        "name": "Papilio_xuthus",
        "type": "pest",
        "description": "Swallowtail butterfly species associated primarily with citrus hosts.",
        "symptoms": [
            "Caterpillar feeding can cause leaf loss on suitable host plants"
        ],
        "management": [
            "Confirm the insect before treatment.",
            "Do not apply grape-specific treatment solely from this model label."
        ],
        "prevention": [
            "Inspect leaves and surrounding vegetation.",
            "Seek expert identification if found on grapevine."
        ],
        "treatment_note": (
            "Not sufficiently verified as a grape-specific pest. "
            "Agricultural expert confirmation is recommended."
        ),
        "verification_status": "NOT VERIFIED as grape-specific",
    },

    "Parathrene_regalis": {
        "name": "Parathrene_regalis",
        "type": "pest",
        "description": "Grape clearwing moth / borer-associated pest.",
        "symptoms": [
            "Boring damage to grapevine wood",
            "Shoot or cane weakening",
            "Possible wilting or breakage"
        ],
        "management": [
            "Inspect trunks, cordons and canes.",
            "Remove severely infested wood where practical.",
            "Monitor adult moth activity.",
            "Use integrated borer-management practices."
        ],
        "prevention": [
            "Remove infested pruning material.",
            "Maintain vineyard sanitation.",
            "Monitor adult moth activity."
        ],
        "treatment_note": (
            "Borer control is most effective when the vulnerable life stage "
            "is targeted; confirm the species before treatment."
        ),
        "verification_status": "grape-associated borer; species confirmation recommended",
    },

    "Phyllocoptes_oleiverus": {
        "name": "Phyllocoptes_oleiverus",
        "type": "pest",
        "description": "Mite label associated primarily with other host crops in the source dataset.",
        "symptoms": [
            "Mite feeding may cause discoloration or surface injury"
        ],
        "management": [
            "Confirm the species before treatment.",
            "Do not automatically apply grape-specific mite treatment."
        ],
        "prevention": [
            "Monitor the affected grapevine carefully.",
            "Seek expert confirmation."
        ],
        "treatment_note": (
            "Not sufficiently verified as a grape-specific pest in this project. "
            "Confirm species before treatment."
        ),
        "verification_status": "NOT VERIFIED as grape-specific",
    },

    "Polyphagotarsonemus_latus": {
        "name": "Polyphagotarsonemus_latus",
        "type": "pest",
        "description": "Broad mite species capable of damaging a wide range of crops.",
        "symptoms": [
            "Distorted young leaves",
            "Stunted new growth",
            "Damage concentrated on tender plant tissues"
        ],
        "management": [
            "Inspect young leaves and shoots.",
            "Confirm mites using magnification.",
            "Remove severely affected growth where practical.",
            "Use appropriate IPM-based mite management."
        ],
        "prevention": [
            "Regular monitoring of new growth.",
            "Avoid unnecessary broad-spectrum pesticide use.",
            "Protect beneficial organisms."
        ],
        "treatment_note": (
            "Use a registered grape mite-management option only after "
            "confirming the pest and current recommendations."
        ),
        "verification_status": "broad mite; grape association documented in some regions",
    },

    "Pseudococcus_comstocki": {
        "name": "Pseudococcus_comstocki",
        "type": "pest",
        "description": "Comstock mealybug associated with grapevine and other hosts.",
        "symptoms": [
            "White waxy insects on plant surfaces",
            "Honeydew deposition",
            "Sooty mold",
            "Weakening of affected vines"
        ],
        "management": [
            "Remove heavily infested plant material where practical.",
            "Maintain vineyard sanitation.",
            "Use biological control where appropriate.",
            "Monitor ants because they can protect mealybugs.",
            "Use spot treatment rather than unnecessary broad-spectrum applications."
        ],
        "prevention": [
            "Inspect trunks, cordons and bunches.",
            "Control ant activity where appropriate.",
            "Maintain vineyard sanitation.",
            "Monitor regularly."
        ],
        "treatment_note": (
            "ICAR-NRCG recommends integrated mealybug management including "
            "biological-control approaches and carefully selected treatments."
        ),
        "verification_status": "grape-associated mealybug; IPM guidance available",
    },

    "Trialeurodes_vaporariorum": {
        "name": "Trialeurodes_vaporariorum",
        "type": "pest",
        "description": "Greenhouse whitefly and broad horticultural pest.",
        "symptoms": [
            "Whitefly adults or nymphs under leaves",
            "Honeydew",
            "Sooty mold",
            "Leaf weakening under heavy infestation"
        ],
        "management": [
            "Inspect the underside of leaves.",
            "Remove heavily infested material where practical.",
            "Use biological control where suitable.",
            "Monitor population levels before intervention."
        ],
        "prevention": [
            "Control weeds and alternate hosts.",
            "Inspect new planting material.",
            "Maintain regular vineyard scouting."
        ],
        "treatment_note": (
            "Confirm that this whitefly is actually responsible for the "
            "grapevine damage before applying pest-specific treatment."
        ),
        "verification_status": "horticultural pest; grape-specific treatment requires confirmation",
    },

    "Viteus_vitifoliae": {
        "name": "Viteus_vitifoliae",
        "type": "pest",
        "description": "Grape phylloxera, a major grapevine pest.",
        "symptoms": [
            "Root damage",
            "Root nodules or swellings",
            "Reduced vine vigor",
            "Possible vine decline"
        ],
        "management": [
            "Use resistant or phylloxera-tolerant rootstocks where appropriate.",
            "Use certified planting material.",
            "Confirm infestation before treatment.",
            "Remove and manage severely affected planting material where appropriate."
        ],
        "prevention": [
            "Use certified planting material.",
            "Use suitable resistant rootstocks.",
            "Avoid movement of contaminated soil or planting material."
        ],
        "treatment_note": (
            "Rootstock selection is an important long-term management strategy. "
            "Chemical control depends on local regulations and infestation conditions."
        ),
        "verification_status": "major grape pest; grape-specific management available",
    },

    "Xylotrechus": {
        "name": "Xylotrechus",
        "type": "pest",
        "description": "Grape-boring beetle genus; exact species should be confirmed.",
        "symptoms": [
            "Boring tunnels in grapevine wood",
            "Cane or trunk weakening",
            "Wilting or dieback of affected wood"
        ],
        "management": [
            "Inspect trunks, cordons and canes.",
            "Remove severely infested wood.",
            "Remove pruning material from the vineyard.",
            "Monitor adult emergence where possible.",
            "Use integrated borer-management practices."
        ],
        "prevention": [
            "Maintain vineyard sanitation.",
            "Remove infested wood.",
            "Monitor adult emergence.",
            "Avoid leaving infested pruning material in the vineyard."
        ],
        "treatment_note": (
            "Xylotrechus includes multiple species. Confirm the exact species "
            "before applying species-specific chemical treatment."
        ),
        "verification_status": "grape-associated genus; exact species confirmation required",
    },
}


# ==========================================================
# HELPER FUNCTIONS
# ==========================================================

def get_recommendation(class_name):
    """
    Return treatment/management information for one class.
    """
    return TREATMENT_DATABASE.get(class_name)


def get_all_diseases():
    """
    Return all disease entries.
    """
    return {
        name: data
        for name, data in TREATMENT_DATABASE.items()
        if data["type"] == "disease"
    }


def get_all_pests():
    """
    Return all pest entries.
    """
    return {
        name: data
        for name, data in TREATMENT_DATABASE.items()
        if data["type"] == "pest"
    }


def get_all_classes():
    """
    Return all 24 model classes.
    """
    return list(TREATMENT_DATABASE.keys())