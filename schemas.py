# Questo blocco pydantic verrà usato nelle versioni 3 e 4 dell'estrazione (LLM+Pydantic e agente React+Pydantic) per forzare 
# a rispettare il formato di output
from pydantic import BaseModel, Field
from typing import List, Literal, Optional

# Definisco i Literal, in questo modo l'LLM non creerà un JSON che contiene Entità e relazioni
# diverse da queste
LabelEntita = Literal["Case", "Person", "Location", "Weapon", "Evidence", "Statement", "Motive", "Charge"]
TipoRelazione = Literal["COMMITTED", "IS_SUSPECTED_IN", "IS_VICTIM_OF", "INVESTIGATES", "DEFENDS", "INVOLVED_IN", "OCCURRED_AT", "WITHIN", "USED_IN", "FOUND_AT", "HAS_MOTIVE", "OWNS_WEAPON", "LEFT_EVIDENCE", "LOCATED_IN", "MADE_STATEMENT", "RELATES_TO", "CHARGED_WITH", "INCLUDES_CHARGE"]

class Entita(BaseModel):
    id: str = Field(description="Format: prefix_name. E.g., 'person_mario_rossi' in lowercase, no spaces.")
    label: LabelEntita = Field(description="The semantic label of the node.")
    name: str = Field(description="The readable name of the entity.")
    
    #Campi opzionali per i nodi Person
    role: Optional[str] = Field(default=None, description="Role in the case (only for Person), otherwise null.")
    gender: Optional[str] = Field(default=None, description="Gender (only for Person), otherwise null.")
    age: Optional[str] = Field(default=None, description="Age if explicitly mentioned (only for Person), otherwise null.")
    profession: Optional[str] = Field(default=None, description="Profession if explicitly mentioned (only for Person), otherwise null.")
    date_of_birth: Optional[str] = Field(default=None, description="Date of birth if explicitly mentioned (only for Person), otherwise null.")
    date_of_death: Optional[str] = Field(default=None, description="Date of death if explicitly mentioned (only for Person), otherwise null.")
    is_deceased: Optional[bool] = Field(default=None, description="True if deceased, False if alive, null for non-Person labels.")

class Relazione(BaseModel):
    source_id: str = Field(description="ID of the starting node (must exist in entities).")
    target_id: str = Field(description="ID of the target node (must exist in entities).")
    type: TipoRelazione = Field(description="The type of relationship.")

class SchemaGrafo(BaseModel):
    entities: List[Entita]
    relationships: List[Relazione]