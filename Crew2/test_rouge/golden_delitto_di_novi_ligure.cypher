// --- NODI ---
MERGE (n_case_delitto_di_novi_ligure:Case {id: "case_delitto_di_novi_ligure"})
SET n_case_delitto_di_novi_ligure.name = "Delitto di Novi Ligure"
MERGE (n_person_erika_de_nardo:Person {id: "person_erika_de_nardo"})
SET n_person_erika_de_nardo.name = "Erika De Nardo", n_person_erika_de_nardo.role = "Killer", n_person_erika_de_nardo.gender = "Female", n_person_erika_de_nardo.age = "16", n_person_erika_de_nardo.profession = "Student", n_person_erika_de_nardo.is_deceased = false
MERGE (n_person_mauro_favaro:Person {id: "person_mauro_favaro"})
SET n_person_mauro_favaro.name = "Mauro Favaro", n_person_mauro_favaro.role = "Killer", n_person_mauro_favaro.gender = "Male", n_person_mauro_favaro.age = "17", n_person_mauro_favaro.is_deceased = false
MERGE (n_person_susanna_cassini:Person {id: "person_susanna_cassini"})
SET n_person_susanna_cassini.name = "Susanna Cassini", n_person_susanna_cassini.role = "Victim", n_person_susanna_cassini.gender = "Female", n_person_susanna_cassini.age = "41", n_person_susanna_cassini.profession = "Accountant", n_person_susanna_cassini.date_of_death = "2001-02-21", n_person_susanna_cassini.is_deceased = true
MERGE (n_person_gianluca_de_nardo:Person {id: "person_gianluca_de_nardo"})
SET n_person_gianluca_de_nardo.name = "Gianluca De Nardo", n_person_gianluca_de_nardo.role = "Victim", n_person_gianluca_de_nardo.gender = "Male", n_person_gianluca_de_nardo.age = "11", n_person_gianluca_de_nardo.date_of_death = "2001-02-21", n_person_gianluca_de_nardo.is_deceased = true
MERGE (n_person_francesco_de_nardo:Person {id: "person_francesco_de_nardo"})
SET n_person_francesco_de_nardo.name = "Francesco De Nardo", n_person_francesco_de_nardo.role = "Target", n_person_francesco_de_nardo.gender = "Male", n_person_francesco_de_nardo.age = "45", n_person_francesco_de_nardo.profession = "Engineer and Manager", n_person_francesco_de_nardo.is_deceased = false
MERGE (n_person_cezar_tellalli:Person {id: "person_cezar_tellalli"})
SET n_person_cezar_tellalli.name = "Cezar Tellalli", n_person_cezar_tellalli.role = "Suspect", n_person_cezar_tellalli.gender = "Male", n_person_cezar_tellalli.age = "17", n_person_cezar_tellalli.is_deceased = false
MERGE (n_person_mario_boccassi:Person {id: "person_mario_boccassi"})
SET n_person_mario_boccassi.name = "Mario Boccassi", n_person_mario_boccassi.role = "Lawyer", n_person_mario_boccassi.gender = "Male", n_person_mario_boccassi.profession = "Lawyer", n_person_mario_boccassi.is_deceased = false
MERGE (n_person_cesare_zaccone:Person {id: "person_cesare_zaccone"})
SET n_person_cesare_zaccone.name = "Cesare Zaccone", n_person_cesare_zaccone.role = "Lawyer", n_person_cesare_zaccone.gender = "Male", n_person_cesare_zaccone.profession = "Lawyer", n_person_cesare_zaccone.is_deceased = false
MERGE (n_person_vittorio_gatti:Person {id: "person_vittorio_gatti"})
SET n_person_vittorio_gatti.name = "Vittorio Gatti", n_person_vittorio_gatti.role = "Lawyer", n_person_vittorio_gatti.gender = "Male", n_person_vittorio_gatti.profession = "Lawyer", n_person_vittorio_gatti.is_deceased = false
MERGE (n_person_lorenzo_repetti:Person {id: "person_lorenzo_repetti"})
SET n_person_lorenzo_repetti.name = "Lorenzo Repetti", n_person_lorenzo_repetti.role = "Lawyer", n_person_lorenzo_repetti.gender = "Male", n_person_lorenzo_repetti.profession = "Lawyer", n_person_lorenzo_repetti.is_deceased = false
MERGE (n_person_livia_locci:Person {id: "person_livia_locci"})
SET n_person_livia_locci.name = "Livia Locci", n_person_livia_locci.role = "Prosecutor", n_person_livia_locci.gender = "Female", n_person_livia_locci.profession = "Public Prosecutor", n_person_livia_locci.is_deceased = false
MERGE (n_person_graziana_calcagno:Person {id: "person_graziana_calcagno"})
SET n_person_graziana_calcagno.name = "Graziana Calcagno", n_person_graziana_calcagno.role = "Judge", n_person_graziana_calcagno.gender = "Female", n_person_graziana_calcagno.profession = "Magistrate", n_person_graziana_calcagno.is_deceased = false
MERGE (n_person_mario_gugole:Person {id: "person_mario_gugole"})
SET n_person_mario_gugole.name = "Mario Gugole", n_person_mario_gugole.role = "Witness", n_person_mario_gugole.gender = "Male", n_person_mario_gugole.profession = "Musician", n_person_mario_gugole.date_of_death = "2008-10", n_person_mario_gugole.is_deceased = true
MERGE (n_person_antonio_mazzi:Person {id: "person_antonio_mazzi"})
SET n_person_antonio_mazzi.name = "Antonio Mazzi", n_person_antonio_mazzi.role = "Witness", n_person_antonio_mazzi.gender = "Male", n_person_antonio_mazzi.profession = "Priest", n_person_antonio_mazzi.is_deceased = false
MERGE (n_location_novi_ligure:Location {id: "location_novi_ligure"})
SET n_location_novi_ligure.name = "Novi Ligure"
MERGE (n_location_alessandria:Location {id: "location_alessandria"})
SET n_location_alessandria.name = "Alessandria"
MERGE (n_location_via_don_beniamino_dacatra_12:Location {id: "location_via_don_beniamino_dacatra_12"})
SET n_location_via_don_beniamino_dacatra_12.name = "via don Beniamino Dacatra, 12"
MERGE (n_location_torino:Location {id: "location_torino"})
SET n_location_torino.name = "Torino"
MERGE (n_location_milano:Location {id: "location_milano"})
SET n_location_milano.name = "Milano"
MERGE (n_location_toscana:Location {id: "location_toscana"})
SET n_location_toscana.name = "Toscana"
MERGE (n_location_lonato:Location {id: "location_lonato"})
SET n_location_lonato.name = "Lonato"
MERGE (n_location_rieti:Location {id: "location_rieti"})
SET n_location_rieti.name = "Rieti"
MERGE (n_weapon_kitchen_knives:Weapon {id: "weapon_kitchen_knives"})
SET n_weapon_kitchen_knives.name = "kitchen knives"
MERGE (n_evidence_blood:Evidence {id: "evidence_blood"})
SET n_evidence_blood.name = "blood traces"
MERGE (n_evidence_gloves:Evidence {id: "evidence_gloves"})
SET n_evidence_gloves.name = "gloves"
MERGE (n_evidence_footprints:Evidence {id: "evidence_footprints"})
SET n_evidence_footprints.name = "bloody footprints"
MERGE (n_evidence_rat_poison:Evidence {id: "evidence_rat_poison"})
SET n_evidence_rat_poison.name = "rat poison powder"
MERGE (n_statement_erika_robbery:Statement {id: "statement_erika_robbery"})
SET n_statement_erika_robbery.name = "Two Albanian burglars committed a robbery and murder"
MERGE (n_statement_omar_bite:Statement {id: "statement_omar_bite"})
SET n_statement_omar_bite.name = "Omar's hand injury was caused by a bite from Gianluca"
MERGE (n_motive_school_performance:Motive {id: "motive_school_performance"})
SET n_motive_school_performance.name = "School performance conflicts and family friction"
MERGE (n_charge_voluntary_manslaughter:Charge {id: "charge_voluntary_manslaughter"})
SET n_charge_voluntary_manslaughter.name = "Duplice omicidio premeditato"

// --- RELAZIONI ---
MATCH (s {id: "person_erika_de_nardo"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_mauro_favaro"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_susanna_cassini"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "person_gianluca_de_nardo"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "person_cezar_tellalli"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_livia_locci"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_graziana_calcagno"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_mario_boccassi"}), (t {id: "person_erika_de_nardo"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_cesare_zaccone"}), (t {id: "person_erika_de_nardo"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_vittorio_gatti"}), (t {id: "person_mauro_favaro"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_lorenzo_repetti"}), (t {id: "person_mauro_favaro"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "case_delitto_di_novi_ligure"}), (t {id: "location_novi_ligure"})
MERGE (s)-[:OCCURRED_AT]->(t)
MATCH (s {id: "location_novi_ligure"}), (t {id: "location_alessandria"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_via_don_beniamino_dacatra_12"}), (t {id: "location_novi_ligure"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "weapon_kitchen_knives"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:USED_IN]->(t)
MATCH (s {id: "weapon_kitchen_knives"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_blood"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_gloves"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_footprints"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_rat_poison"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "case_delitto_di_novi_ligure"}), (t {id: "motive_school_performance"})
MERGE (s)-[:HAS_MOTIVE]->(t)
MATCH (s {id: "person_erika_de_nardo"}), (t {id: "evidence_blood"})
MERGE (s)-[:LEFT_EVIDENCE]->(t)
MATCH (s {id: "person_mauro_favaro"}), (t {id: "evidence_blood"})
MERGE (s)-[:LEFT_EVIDENCE]->(t)
MATCH (s {id: "person_erika_de_nardo"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:LOCATED_IN]->(t)
MATCH (s {id: "person_mauro_favaro"}), (t {id: "location_via_don_beniamino_dacatra_12"})
MERGE (s)-[:LOCATED_IN]->(t)
MATCH (s {id: "person_erika_de_nardo"}), (t {id: "statement_erika_robbery"})
MERGE (s)-[:MADE_STATEMENT]->(t)
MATCH (s {id: "person_mauro_favaro"}), (t {id: "statement_omar_bite"})
MERGE (s)-[:MADE_STATEMENT]->(t)
MATCH (s {id: "statement_erika_robbery"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:RELATES_TO]->(t)
MATCH (s {id: "statement_omar_bite"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:RELATES_TO]->(t)
MATCH (s {id: "person_erika_de_nardo"}), (t {id: "charge_voluntary_manslaughter"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "person_mauro_favaro"}), (t {id: "charge_voluntary_manslaughter"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "case_delitto_di_novi_ligure"}), (t {id: "charge_voluntary_manslaughter"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)
MATCH (s {id: "person_erika_de_nardo"}), (t {id: "weapon_kitchen_knives"})
MERGE (s)-[:OWNS_WEAPON]->(t)
MATCH (s {id: "person_susanna_cassini"}), (t {id: "weapon_kitchen_knives"})
MERGE (s)-[:OWNS_WEAPON]->(t)
MATCH (s {id: "person_francesco_de_nardo"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_mario_gugole"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_antonio_mazzi"}), (t {id: "case_delitto_di_novi_ligure"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "location_torino"}), (t {id: "location_alessandria"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_milano"}), (t {id: "location_lonato"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_rieti"}), (t {id: "location_lazio"})
MERGE (s)-[:WITHIN]->(t)