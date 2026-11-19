// --- NODI ---
MERGE (n_case_omicidio_marco_vannini:Case {id: "case_omicidio_marco_vannini"})
SET n_case_omicidio_marco_vannini.name = "Omicidio di Marco Vannini"
MERGE (n_person_marco_vannini:Person {id: "person_marco_vannini"})
SET n_person_marco_vannini.name = "Marco Vannini", n_person_marco_vannini.role = "Victim", n_person_marco_vannini.gender = "Male", n_person_marco_vannini.age = "20", n_person_marco_vannini.is_deceased = true
MERGE (n_person_antonio_ciontoli:Person {id: "person_antonio_ciontoli"})
SET n_person_antonio_ciontoli.name = "Antonio Ciontoli", n_person_antonio_ciontoli.role = "Suspect", n_person_antonio_ciontoli.gender = "Male", n_person_antonio_ciontoli.profession = "sottufficiale della Marina Militare", n_person_antonio_ciontoli.is_deceased = false
MERGE (n_person_martina_ciontoli:Person {id: "person_martina_ciontoli"})
SET n_person_martina_ciontoli.name = "Martina Ciontoli", n_person_martina_ciontoli.role = "Suspect", n_person_martina_ciontoli.gender = "Female", n_person_martina_ciontoli.is_deceased = false
MERGE (n_person_maria_pezzillo:Person {id: "person_maria_pezzillo"})
SET n_person_maria_pezzillo.name = "Maria Pezzillo", n_person_maria_pezzillo.role = "Suspect", n_person_maria_pezzillo.gender = "Female", n_person_maria_pezzillo.is_deceased = false
MERGE (n_person_federico_ciontoli:Person {id: "person_federico_ciontoli"})
SET n_person_federico_ciontoli.name = "Federico Ciontoli", n_person_federico_ciontoli.role = "Suspect", n_person_federico_ciontoli.gender = "Male", n_person_federico_ciontoli.is_deceased = false
MERGE (n_person_viola_giorgini:Person {id: "person_viola_giorgini"})
SET n_person_viola_giorgini.name = "Viola Giorgini", n_person_viola_giorgini.role = "Suspect", n_person_viola_giorgini.gender = "Female", n_person_viola_giorgini.is_deceased = false
MERGE (n_location_ladispoli:Location {id: "location_ladispoli"})
SET n_location_ladispoli.name = "Ladispoli"
MERGE (n_location_roma:Location {id: "location_roma"})
SET n_location_roma.name = "Roma"
MERGE (n_location_casa_ciontoli:Location {id: "location_casa_ciontoli"})
SET n_location_casa_ciontoli.name = "abitazione della famiglia Ciontoli"
MERGE (n_location_ospedale_ladispoli:Location {id: "location_ospedale_ladispoli"})
SET n_location_ospedale_ladispoli.name = "ospedale di Ladispoli"
MERGE (n_weapon_pistola:Weapon {id: "weapon_pistola"})
SET n_weapon_pistola.name = "pistola calibro 9 parabellum"
MERGE (n_evidence_bossoli:Evidence {id: "evidence_bossoli"})
SET n_evidence_bossoli.name = "bossoli"
MERGE (n_evidence_tracce_sangue:Evidence {id: "evidence_tracce_sangue"})
SET n_evidence_tracce_sangue.name = "tracce di sangue"
MERGE (n_charge_omicidio_volontario:Charge {id: "charge_omicidio_volontario"})
SET n_charge_omicidio_volontario.name = "omicidio volontario con dolo eventuale"
MERGE (n_charge_concorso_omicidio_volontario:Charge {id: "charge_concorso_omicidio_volontario"})
SET n_charge_concorso_omicidio_volontario.name = "concorso in omicidio volontario"
MERGE (n_charge_concorso_omicidio_colposo:Charge {id: "charge_concorso_omicidio_colposo"})
SET n_charge_concorso_omicidio_colposo.name = "concorso in omicidio colposo"

// --- RELAZIONI ---
MATCH (s {id: "person_antonio_ciontoli"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_marco_vannini"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "person_martina_ciontoli"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_maria_pezzillo"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_federico_ciontoli"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_viola_giorgini"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "case_omicidio_marco_vannini"}), (t {id: "location_ladispoli"})
MERGE (s)-[:OCCURRED_AT]->(t)
MATCH (s {id: "location_ladispoli"}), (t {id: "location_roma"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_casa_ciontoli"}), (t {id: "location_ladispoli"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_ospedale_ladispoli"}), (t {id: "location_ladispoli"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "weapon_pistola"}), (t {id: "case_omicidio_marco_vannini"})
MERGE (s)-[:USED_IN]->(t)
MATCH (s {id: "weapon_pistola"}), (t {id: "location_casa_ciontoli"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_bossoli"}), (t {id: "location_casa_ciontoli"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_tracce_sangue"}), (t {id: "location_casa_ciontoli"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "person_antonio_ciontoli"}), (t {id: "weapon_pistola"})
MERGE (s)-[:OWNS_WEAPON]->(t)
MATCH (s {id: "person_antonio_ciontoli"}), (t {id: "charge_omicidio_volontario"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_martina_ciontoli"}), (t {id: "charge_concorso_omicidio_volontario"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_martina_ciontoli"}), (t {id: "charge_concorso_omicidio_colposo"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_maria_pezzillo"}), (t {id: "charge_concorso_omicidio_volontario"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_maria_pezzillo"}), (t {id: "charge_concorso_omicidio_colposo"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_federico_ciontoli"}), (t {id: "charge_concorso_omicidio_volontario"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_federico_ciontoli"}), (t {id: "charge_concorso_omicidio_colposo"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_viola_giorgini"}), (t {id: "charge_concorso_omicidio_volontario"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_viola_giorgini"}), (t {id: "charge_concorso_omicidio_colposo"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "case_omicidio_marco_vannini"}), (t {id: "charge_omicidio_volontario"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_marco_vannini"}), (t {id: "charge_concorso_omicidio_volontario"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_marco_vannini"}), (t {id: "charge_concorso_omicidio_colposo"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)