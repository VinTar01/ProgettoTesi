// --- NODI ---
MERGE (n_case_omicidio_di_giulia_cecchettin:Case {id: "case_omicidio_di_giulia_cecchettin"})
SET n_case_omicidio_di_giulia_cecchettin.name = "Omicidio di Giulia Cecchettin"
MERGE (n_person_giulia_cecchettin:Person {id: "person_giulia_cecchettin"})
SET n_person_giulia_cecchettin.name = "Giulia Cecchettin", n_person_giulia_cecchettin.role = "Victim", n_person_giulia_cecchettin.gender = "Female", n_person_giulia_cecchettin.age = "22", n_person_giulia_cecchettin.profession = "studentessa", n_person_giulia_cecchettin.date_of_birth = "5 maggio 2001", n_person_giulia_cecchettin.date_of_death = "11 novembre 2023", n_person_giulia_cecchettin.is_deceased = true
MERGE (n_person_filippo_turetta:Person {id: "person_filippo_turetta"})
SET n_person_filippo_turetta.name = "Filippo Turetta", n_person_filippo_turetta.role = "Suspect", n_person_filippo_turetta.gender = "Male", n_person_filippo_turetta.date_of_birth = "18 dicembre 2001", n_person_filippo_turetta.is_deceased = false
MERGE (n_person_gino_cecchettin:Person {id: "person_gino_cecchettin"})
SET n_person_gino_cecchettin.name = "Gino Cecchettin", n_person_gino_cecchettin.role = "Relative", n_person_gino_cecchettin.gender = "Male", n_person_gino_cecchettin.profession = "ingegnere", n_person_gino_cecchettin.date_of_birth = "3 settembre 1968", n_person_gino_cecchettin.is_deceased = false
MERGE (n_person_elena_cecchettin:Person {id: "person_elena_cecchettin"})
SET n_person_elena_cecchettin.name = "Elena Cecchettin", n_person_elena_cecchettin.role = "Relative", n_person_elena_cecchettin.gender = "Female", n_person_elena_cecchettin.date_of_birth = "4 luglio 1999", n_person_elena_cecchettin.is_deceased = false
MERGE (n_person_davide_cecchettin:Person {id: "person_davide_cecchettin"})
SET n_person_davide_cecchettin.name = "Davide Cecchettin", n_person_davide_cecchettin.role = "Relative", n_person_davide_cecchettin.gender = "Male", n_person_davide_cecchettin.date_of_birth = "10 maggio 2006", n_person_davide_cecchettin.is_deceased = false
MERGE (n_person_monica_camerotto:Person {id: "person_monica_camerotto"})
SET n_person_monica_camerotto.name = "Monica Camerotto", n_person_monica_camerotto.role = "Relative", n_person_monica_camerotto.gender = "Female", n_person_monica_camerotto.date_of_birth = "5 agosto 1971", n_person_monica_camerotto.date_of_death = "20 ottobre 2022", n_person_monica_camerotto.is_deceased = true
MERGE (n_person_stefano_tigani:Person {id: "person_stefano_tigani"})
SET n_person_stefano_tigani.name = "Stefano Tigani", n_person_stefano_tigani.role = "Lawyer", n_person_stefano_tigani.gender = "Male", n_person_stefano_tigani.profession = "avvocato", n_person_stefano_tigani.is_deceased = false
MERGE (n_person_bruno_cherchi:Person {id: "person_bruno_cherchi"})
SET n_person_bruno_cherchi.name = "Bruno Cherchi", n_person_bruno_cherchi.role = "Prosecutor", n_person_bruno_cherchi.gender = "Male", n_person_bruno_cherchi.profession = "procuratore", n_person_bruno_cherchi.is_deceased = false
MERGE (n_person_andrea_petroni:Person {id: "person_andrea_petroni"})
SET n_person_andrea_petroni.name = "Andrea Petroni", n_person_andrea_petroni.role = "Prosecutor", n_person_andrea_petroni.gender = "Male", n_person_andrea_petroni.profession = "pubblico ministero", n_person_andrea_petroni.is_deceased = false
MERGE (n_person_giovanni_caruso:Person {id: "person_giovanni_caruso"})
SET n_person_giovanni_caruso.name = "Giovanni Caruso", n_person_giovanni_caruso.role = "Lawyer", n_person_giovanni_caruso.gender = "Male", n_person_giovanni_caruso.profession = "avvocato difensore", n_person_giovanni_caruso.is_deceased = false
MERGE (n_person_luca_zaia:Person {id: "person_luca_zaia"})
SET n_person_luca_zaia.name = "Luca Zaia", n_person_luca_zaia.role = "Authority", n_person_luca_zaia.gender = "Male", n_person_luca_zaia.profession = "presidente della regione Veneto", n_person_luca_zaia.is_deceased = false
MERGE (n_person_giuseppe_valditara:Person {id: "person_giuseppe_valditara"})
SET n_person_giuseppe_valditara.name = "Giuseppe Valditara", n_person_giuseppe_valditara.role = "Authority", n_person_giuseppe_valditara.gender = "Male", n_person_giuseppe_valditara.profession = "ministro dell'istruzione", n_person_giuseppe_valditara.is_deceased = false
MERGE (n_person_roberta_metsola:Person {id: "person_roberta_metsola"})
SET n_person_roberta_metsola.name = "Roberta Metsola", n_person_roberta_metsola.role = "Authority", n_person_roberta_metsola.gender = "Female", n_person_roberta_metsola.profession = "Presidente del Parlamento europeo", n_person_roberta_metsola.is_deceased = false
MERGE (n_person_anna_maria_bernini:Person {id: "person_anna_maria_bernini"})
SET n_person_anna_maria_bernini.name = "Anna Maria Bernini", n_person_anna_maria_bernini.role = "Authority", n_person_anna_maria_bernini.gender = "Female", n_person_anna_maria_bernini.profession = "Ministra dell'università e della ricerca", n_person_anna_maria_bernini.is_deceased = false
MERGE (n_person_ursula_von_der_leyen:Person {id: "person_ursula_von_der_leyen"})
SET n_person_ursula_von_der_leyen.name = "Ursula von der Leyen", n_person_ursula_von_der_leyen.role = "Authority", n_person_ursula_von_der_leyen.gender = "Female", n_person_ursula_von_der_leyen.profession = "Presidente della Commissione europea", n_person_ursula_von_der_leyen.is_deceased = false
MERGE (n_person_claudio_cipolla:Person {id: "person_claudio_cipolla"})
SET n_person_claudio_cipolla.name = "Claudio Cipolla", n_person_claudio_cipolla.role = "Authority", n_person_claudio_cipolla.gender = "Male", n_person_claudio_cipolla.profession = "vescovo", n_person_claudio_cipolla.is_deceased = false
MERGE (n_person_carlo_nordio:Person {id: "person_carlo_nordio"})
SET n_person_carlo_nordio.name = "Carlo Nordio", n_person_carlo_nordio.role = "Authority", n_person_carlo_nordio.gender = "Male", n_person_carlo_nordio.profession = "ministro della giustizia", n_person_carlo_nordio.is_deceased = false
MERGE (n_person_eugenia_maria_roccella:Person {id: "person_eugenia_maria_roccella"})
SET n_person_eugenia_maria_roccella.name = "Eugenia Maria Roccella", n_person_eugenia_maria_roccella.role = "Authority", n_person_eugenia_maria_roccella.gender = "Female", n_person_eugenia_maria_roccella.profession = "Ministra per le pari opportunità e per le politiche per la famiglia", n_person_eugenia_maria_roccella.is_deceased = false
MERGE (n_person_laura_boldrini:Person {id: "person_laura_boldrini"})
SET n_person_laura_boldrini.name = "Laura Boldrini", n_person_laura_boldrini.role = "Authority", n_person_laura_boldrini.gender = "Female", n_person_laura_boldrini.profession = "politica", n_person_laura_boldrini.is_deceased = false
MERGE (n_location_fosso:Location {id: "location_fosso"})
SET n_location_fosso.name = "Fossò"
MERGE (n_location_venezia:Location {id: "location_venezia"})
SET n_location_venezia.name = "Venezia"
MERGE (n_location_padova:Location {id: "location_padova"})
SET n_location_padova.name = "Padova"
MERGE (n_location_vigonovo:Location {id: "location_vigonovo"})
SET n_location_vigonovo.name = "Vigonovo"
MERGE (n_location_germania:Location {id: "location_germania"})
SET n_location_germania.name = "Germania"
MERGE (n_location_verona:Location {id: "location_verona"})
SET n_location_verona.name = "Verona"
MERGE (n_weapon_coltello:Weapon {id: "weapon_coltello"})
SET n_weapon_coltello.name = "lama di un coltello lunga 21 cm"
MERGE (n_evidence_sangue:Evidence {id: "evidence_sangue"})
SET n_evidence_sangue.name = "notevoli quantità di sangue"
MERGE (n_charge_omicidio_volontario:Charge {id: "charge_omicidio_volontario"})
SET n_charge_omicidio_volontario.name = "omicidio volontario"
MERGE (n_charge_sequestro_di_persona:Charge {id: "charge_sequestro_di_persona"})
SET n_charge_sequestro_di_persona.name = "sequestro di persona"
MERGE (n_charge_occultamento_di_cadavere:Charge {id: "charge_occultamento_di_cadavere"})
SET n_charge_occultamento_di_cadavere.name = "occultamento di cadavere"
MERGE (n_charge_premeditazione:Charge {id: "charge_premeditazione"})
SET n_charge_premeditazione.name = "premeditazione"
MERGE (n_charge_crudelta:Charge {id: "charge_crudelta"})
SET n_charge_crudelta.name = "crudeltà"
MERGE (n_charge_stalking:Charge {id: "charge_stalking"})
SET n_charge_stalking.name = "stalking"

// --- RELAZIONI ---
MATCH (s {id: "person_filippo_turetta"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_giulia_cecchettin"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "location_fosso"})
MERGE (s)-[:OCCURRED_AT]->(t)
MATCH (s {id: "location_fosso"}), (t {id: "location_venezia"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "weapon_coltello"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:USED_IN]->(t)
MATCH (s {id: "weapon_coltello"}), (t {id: "location_fosso"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_sangue"}), (t {id: "location_fosso"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "person_stefano_tigani"}), (t {id: "person_gino_cecchettin"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_stefano_tigani"}), (t {id: "person_elena_cecchettin"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_stefano_tigani"}), (t {id: "person_davide_cecchettin"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_bruno_cherchi"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_andrea_petroni"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_giovanni_caruso"}), (t {id: "person_filippo_turetta"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_gino_cecchettin"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_elena_cecchettin"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_davide_cecchettin"}), (t {id: "case_omicidio_di_giulia_cecchettin"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "charge_omicidio_volontario"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "charge_sequestro_di_persona"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "charge_occultamento_di_cadavere"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "charge_premeditazione"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "charge_crudelta"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "case_omicidio_di_giulia_cecchettin"}), (t {id: "charge_stalking"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "person_filippo_turetta"}), (t {id: "charge_omicidio_volontario"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_filippo_turetta"}), (t {id: "charge_sequestro_di_persona"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_filippo_turetta"}), (t {id: "charge_occultamento_di_cadavere"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_filippo_turetta"}), (t {id: "charge_premeditazione"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_filippo_turetta"}), (t {id: "charge_crudelta"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_filippo_turetta"}), (t {id: "charge_stalking"})
MERGE (s)-[:CHARGED_WITH]->(t)