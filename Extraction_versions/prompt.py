
#usato in tutte e 4 le versioni
PROMPT_BASE = """
You are an expert investigative analyst specializing in Knowledge Graphs. 
Your vital task is to extract an EXTREME, EXHAUSTIVE, AND COMPLETE mapping of the following true crime case. 
You cannot afford to omit any physical or logical detail.

Case text to analyze:
--------------------------------------------------
{testo_caso}
--------------------------------------------------

WARNING - NO HALLUCINATIONS AND NO LAZINESS:
1. Extract ONLY explicitly mentioned information. Do not invent anything.
2. NO LAZINESS: You must extract ALL possible nodes present in the text. Do not stop at just people's names. The crime scene (Evidence, Weapon, Location) is more important than the people themselves. If you miss the evidence, the investigation will fail.

MANDATORY LABELS TO SEARCH FOR:
- Case: The criminal event or judicial case (e.g., Garlasco murder).
- Person: Victims, Suspects, Killers, Witnesses, Lawyers, Prosecutors.
- Location: All macro-areas (cities) and micro-environments (rooms, houses).
- Weapon: The murder weapon, if mentioned.
- Evidence: Exclusively physical, biological traces, or material exhibits (blood, bullet casings, fingerprints).
- Statement: Summary of declarations, testimonies, or alibis (e.g., 'Claims to have been working on the computer').
- Motive: The motive (e.g., jealousy, financial reasons, revenge).
- Charge: Formal charges or crimes (e.g., voluntary manslaughter, perjury).

NODE PROPERTY EXTRACTION RULES:
'Person' nodes require the extraction of specific attributes.
- 'gender' and 'role': MANDATORY ONLY if the label is 'Person'. Infer gender from name/pronouns, and role (e.g., Victim, Suspect, Witness, Investigator) from the case context. For all other labels, set these to null.
- 'age', 'profession', 'date_of_birth', 'date_of_death': Extract ONLY IF explicitly written in the text for that person. If not mentioned, return null. Do not invent or deduce unstated data.
- 'is_deceased': Boolean. Set to true ONLY IF the text explicitly states the person is dead (e.g., they are a murder victim). Set to false if they are alive. For all non-Person labels, set this to null.

FUNDAMENTAL RELATIONSHIP RULES (RESPECT THE DIRECTION):
- COMMITTED: Person (Killer/Culprit) -> Case
- IS_SUSPECTED_IN: Person (Suspect) -> Case
- IS_VICTIM_OF: Person (Victim) -> Case
- INVESTIGATES: Person (Prosecutor/Police) -> Case
- DEFENDS: Person (Lawyer) -> Person (Defendant)
- INVOLVED_IN: Person (Witness/Relative) -> Case
- OCCURRED_AT: Case -> Location
- WITHIN: Location (micro) -> Location (macro)
- USED_IN: Weapon -> Case
- FOUND_AT: Evidence/Weapon -> Location
- HAS_MOTIVE: Case -> Motive
- LEFT_EVIDENCE: Person -> Evidence
- LOCATED_IN: Person -> Location
- MADE_STATEMENT: Person -> Statement
- RELATES_TO: Statement -> Case/Location
- CHARGED_WITH: Person -> Charge
- INCLUDES_CHARGE: Case -> Charge
- OWNS_WEAPON: Person -> Weapon

SELF-CONTROL CHECKLIST:
1. Did you map the crime scene? Are there Evidence or Weapon nodes in your graph if they were in the text?
2. Did you invert IS_VICTIM_OF? (Wrong: Case->Person. Correct: Person->Case).
3. Did you invert INCLUDES_CHARGE? (Wrong: Charge->Case. Correct: Case->Charge).
4. Are there orphan nodes? Every entity in 'entities' MUST appear in 'relationships'.

FEW-SHOT EXAMPLE LOGIC:
Text: "In Rome, Detective Rossi found a bloody knife."
Extraction: 
- Entities: Rossi (Person, Male, Investigator, is_deceased: false), Rome (Location), bloody knife (Evidence). 
- Relationships: Rossi LOCATED_IN Rome, bloody knife FOUND_AT Rome.
"""

# Il formato (Come estrarre). Usato nelle varianti 1 e 2(LLM e ReActOnly) 
#le varianti 3 e 4 useranno il file schemas.py
PROMPT_STRUTTURA = """
REQUIRED OUTPUT FORMAT:
Return EXCLUSIVELY a valid JSON block that strictly respects this schema:
```json
{
  "entities": [
    {
      "id": "unique lowercase string with underscore and prefix (e.g., 'weapon_blunt_object')",
      "label": "one of the mandatory labels above",
      "name": "readable name",
      "role": "if label is Person insert role (e.g., Victim), otherwise null",
      "gender": "if label is Person insert gender (e.g., Male/Female), otherwise null",
      "age": "age if mentioned in text, otherwise null",
      "profession": "profession if mentioned, otherwise null",
      "date_of_birth": "date of birth if mentioned in text, otherwise null",
      "date_of_death": "date of death if mentioned in text, otherwise null",
      "is_deceased": "true if person is dead, false if alive, null if not a Person"
    }
  ],
  "relationships": [
    {
      "source_id": "exact id of the starting node",
      "target_id": "exact id of the target node",
      "type": "one of the mandatory relationships above"
    }
  ]
}
"""