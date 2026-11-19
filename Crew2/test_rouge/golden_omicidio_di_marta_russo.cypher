// --- NODI ---
MERGE (n_case_omicidio_marta_russo:Case {id: "case_omicidio_marta_russo"})
SET n_case_omicidio_marta_russo.name = "Omicidio di Marta Russo"
MERGE (n_person_marta_russo:Person {id: "person_marta_russo"})
SET n_person_marta_russo.name = "Marta Russo", n_person_marta_russo.role = "Victim", n_person_marta_russo.gender = "Female", n_person_marta_russo.age = "22", n_person_marta_russo.profession = "Student", n_person_marta_russo.date_of_birth = "1975-04-13", n_person_marta_russo.date_of_death = "1997-05-14", n_person_marta_russo.is_deceased = true
MERGE (n_person_giovanni_scattone:Person {id: "person_giovanni_scattone"})
SET n_person_giovanni_scattone.name = "Giovanni Scattone", n_person_giovanni_scattone.role = "Suspect", n_person_giovanni_scattone.gender = "Male", n_person_giovanni_scattone.age = "29", n_person_giovanni_scattone.profession = "University Assistant", n_person_giovanni_scattone.is_deceased = false
MERGE (n_person_salvatore_ferraro:Person {id: "person_salvatore_ferraro"})
SET n_person_salvatore_ferraro.name = "Salvatore Ferraro", n_person_salvatore_ferraro.role = "Suspect", n_person_salvatore_ferraro.gender = "Male", n_person_salvatore_ferraro.age = "30", n_person_salvatore_ferraro.profession = "University Assistant", n_person_salvatore_ferraro.is_deceased = false
MERGE (n_person_francesco_liparota:Person {id: "person_francesco_liparota"})
SET n_person_francesco_liparota.name = "Francesco Liparota", n_person_francesco_liparota.role = "Suspect", n_person_francesco_liparota.gender = "Male", n_person_francesco_liparota.age = "35", n_person_francesco_liparota.profession = "Janitor", n_person_francesco_liparota.is_deceased = false
MERGE (n_person_gabriella_alletto:Person {id: "person_gabriella_alletto"})
SET n_person_gabriella_alletto.name = "Gabriella Alletto", n_person_gabriella_alletto.role = "Witness", n_person_gabriella_alletto.gender = "Female", n_person_gabriella_alletto.age = "45", n_person_gabriella_alletto.profession = "Administrative Employee", n_person_gabriella_alletto.is_deceased = false
MERGE (n_person_jolanda_ricci:Person {id: "person_jolanda_ricci"})
SET n_person_jolanda_ricci.name = "Jolanda Ricci", n_person_jolanda_ricci.role = "Witness", n_person_jolanda_ricci.gender = "Female", n_person_jolanda_ricci.profession = "Student", n_person_jolanda_ricci.is_deceased = false
MERGE (n_person_maria_chiara_lipari:Person {id: "person_maria_chiara_lipari"})
SET n_person_maria_chiara_lipari.name = "Maria Chiara Lipari", n_person_maria_chiara_lipari.role = "Witness", n_person_maria_chiara_lipari.gender = "Female", n_person_maria_chiara_lipari.profession = "PhD Student", n_person_maria_chiara_lipari.is_deceased = false
MERGE (n_person_bruno_romano:Person {id: "person_bruno_romano"})
SET n_person_bruno_romano.name = "Bruno Romano", n_person_bruno_romano.role = "Suspect", n_person_bruno_romano.gender = "Male", n_person_bruno_romano.profession = "Professor", n_person_bruno_romano.is_deceased = false
MERGE (n_person_carmelo_zingale:Person {id: "person_carmelo_zingale"})
SET n_person_carmelo_zingale.name = "Carmelo Zingale", n_person_carmelo_zingale.role = "Suspect", n_person_carmelo_zingale.gender = "Male", n_person_carmelo_zingale.profession = "Librarian", n_person_carmelo_zingale.is_deceased = false
MERGE (n_person_giulia_bongiorno:Person {id: "person_giulia_bongiorno"})
SET n_person_giulia_bongiorno.name = "Giulia Bongiorno", n_person_giulia_bongiorno.role = "Lawyer", n_person_giulia_bongiorno.gender = "Female", n_person_giulia_bongiorno.profession = "Lawyer", n_person_giulia_bongiorno.is_deceased = false
MERGE (n_person_franco_coppi:Person {id: "person_franco_coppi"})
SET n_person_franco_coppi.name = "Franco Coppi", n_person_franco_coppi.role = "Lawyer", n_person_franco_coppi.gender = "Male", n_person_franco_coppi.profession = "Lawyer", n_person_franco_coppi.is_deceased = false
MERGE (n_person_italo_ormanni:Person {id: "person_italo_ormanni"})
SET n_person_italo_ormanni.name = "Italo Ormanni", n_person_italo_ormanni.role = "Prosecutor", n_person_italo_ormanni.gender = "Male", n_person_italo_ormanni.profession = "Prosecutor", n_person_italo_ormanni.is_deceased = false
MERGE (n_person_carlo_lasperanza:Person {id: "person_carlo_lasperanza"})
SET n_person_carlo_lasperanza.name = "Carlo Lasperanza", n_person_carlo_lasperanza.role = "Prosecutor", n_person_carlo_lasperanza.gender = "Male", n_person_carlo_lasperanza.profession = "Prosecutor", n_person_carlo_lasperanza.is_deceased = false
MERGE (n_location_citta_universitaria:Location {id: "location_citta_universitaria"})
SET n_location_citta_universitaria.name = "Città Universitaria della Sapienza"
MERGE (n_location_roma:Location {id: "location_roma"})
SET n_location_roma.name = "Roma"
MERGE (n_location_aula_6:Location {id: "location_aula_6"})
SET n_location_aula_6.name = "Aula Assistenti dell'Istituto di filosofia del diritto"
MERGE (n_weapon_pistola_calibro_22:Weapon {id: "weapon_pistola_calibro_22"})
SET n_weapon_pistola_calibro_22.name = "Pistola calibro .22"
MERGE (n_evidence_proiettile:Evidence {id: "evidence_proiettile"})
SET n_evidence_proiettile.name = "Proiettile calibro .22"
MERGE (n_evidence_particella_bario_antimonio:Evidence {id: "evidence_particella_bario_antimonio"})
SET n_evidence_particella_bario_antimonio.name = "Particella di ferro-bario-antimonio"
MERGE (n_charge_omicidio_colposo:Charge {id: "charge_omicidio_colposo"})
SET n_charge_omicidio_colposo.name = "Omicidio colposo aggravato"
MERGE (n_charge_favoreggiamento:Charge {id: "charge_favoreggiamento"})
SET n_charge_favoreggiamento.name = "Favoreggiamento personale"
MERGE (n_motive_nessun_movente:Motive {id: "motive_nessun_movente"})
SET n_motive_nessun_movente.name = "Assenza di movente / Futili motivi / Sbaglio accidentale"
MERGE (n_statement_alletto_accusa:Statement {id: "statement_alletto_accusa"})
SET n_statement_alletto_accusa.name = "Dichiarazioni di accusa di Gabriella Alletto contro Scattone e Ferraro"

// --- RELAZIONI ---
MATCH (s {id: "person_marta_russo"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "person_giovanni_scattone"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_salvatore_ferraro"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_italo_ormanni"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_carlo_lasperanza"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_bruno_romano"}), (t {id: "person_giulia_bongiorno"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_bruno_romano"}), (t {id: "person_franco_coppi"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "case_omicidio_marta_russo"}), (t {id: "location_citta_universitaria"})
MERGE (s)-[:OCCURRED_AT]->(t)
MATCH (s {id: "location_citta_universitaria"}), (t {id: "location_roma"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_aula_6"}), (t {id: "location_citta_universitaria"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "weapon_pistola_calibro_22"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:USED_IN]->(t)
MATCH (s {id: "evidence_proiettile"}), (t {id: "location_citta_universitaria"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_particella_bario_antimonio"}), (t {id: "location_aula_6"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "case_omicidio_marta_russo"}), (t {id: "motive_nessun_movente"})
MERGE (s)-[:HAS_MOTIVE]->(t)
MATCH (s {id: "person_gabriella_alletto"}), (t {id: "statement_alletto_accusa"})
MERGE (s)-[:MADE_STATEMENT]->(t)
MATCH (s {id: "statement_alletto_accusa"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:RELATES_TO]->(t)
MATCH (s {id: "person_giovanni_scattone"}), (t {id: "charge_omicidio_colposo"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_salvatore_ferraro"}), (t {id: "charge_favoreggiamento"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "case_omicidio_marta_russo"}), (t {id: "charge_omicidio_colposo"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_marta_russo"}), (t {id: "charge_favoreggiamento"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "person_jolanda_ricci"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_maria_chiara_lipari"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_francesco_liparota"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_bruno_romano"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_carmelo_zingale"}), (t {id: "case_omicidio_marta_russo"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_marta_russo"}), (t {id: "location_citta_universitaria"})
MERGE (s)-[:LOCATED_IN]->(t)
MATCH (s {id: "person_giovanni_scattone"}), (t {id: "location_aula_6"})
MERGE (s)-[:LOCATED_IN]->(t)
MATCH (s {id: "person_salvatore_ferraro"}), (t {id: "location_aula_6"})
MERGE (s)-[:LOCATED_IN]->(t)