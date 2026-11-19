// --- NODI ---
MERGE (n_case_delitto_di_cogne:Case {id: "case_delitto_di_cogne"})
SET n_case_delitto_di_cogne.name = "Delitto di Cogne"
MERGE (n_person_samuele_lorenzi:Person {id: "person_samuele_lorenzi"})
SET n_person_samuele_lorenzi.name = "Samuele Lorenzi", n_person_samuele_lorenzi.role = "Victim", n_person_samuele_lorenzi.gender = "Male", n_person_samuele_lorenzi.age = "3", n_person_samuele_lorenzi.date_of_death = "January 30, 2002", n_person_samuele_lorenzi.is_deceased = true
MERGE (n_person_annamaria_franzoni:Person {id: "person_annamaria_franzoni"})
SET n_person_annamaria_franzoni.name = "Annamaria Franzoni", n_person_annamaria_franzoni.role = "Suspect", n_person_annamaria_franzoni.gender = "Female", n_person_annamaria_franzoni.is_deceased = false
MERGE (n_person_davide_lorenzi:Person {id: "person_davide_lorenzi"})
SET n_person_davide_lorenzi.name = "Davide Lorenzi", n_person_davide_lorenzi.role = "Witness", n_person_davide_lorenzi.gender = "Male", n_person_davide_lorenzi.is_deceased = false
MERGE (n_person_ada_satragni:Person {id: "person_ada_satragni"})
SET n_person_ada_satragni.name = "Ada Satragni", n_person_ada_satragni.role = "Witness", n_person_ada_satragni.gender = "Female", n_person_ada_satragni.is_deceased = false
MERGE (n_person_maria_carla_davieri:Person {id: "person_maria_carla_davieri"})
SET n_person_maria_carla_davieri.name = "Maria Carla Davieri", n_person_maria_carla_davieri.role = "Prosecutor", n_person_maria_carla_davieri.gender = "Female", n_person_maria_carla_davieri.profession = "Prosecutor", n_person_maria_carla_davieri.is_deceased = false
MERGE (n_person_carlo_taormina:Person {id: "person_carlo_taormina"})
SET n_person_carlo_taormina.name = "Carlo Taormina", n_person_carlo_taormina.role = "Lawyer", n_person_carlo_taormina.gender = "Male", n_person_carlo_taormina.profession = "Lawyer", n_person_carlo_taormina.is_deceased = false
MERGE (n_person_paola_savio:Person {id: "person_paola_savio"})
SET n_person_paola_savio.name = "Paola Savio", n_person_paola_savio.role = "Lawyer", n_person_paola_savio.gender = "Female", n_person_paola_savio.profession = "Lawyer", n_person_paola_savio.is_deceased = false
MERGE (n_location_cogne:Location {id: "location_cogne"})
SET n_location_cogne.name = "Cogne"
MERGE (n_location_aosta_valley:Location {id: "location_aosta_valley"})
SET n_location_aosta_valley.name = "Aosta Valley"
MERGE (n_location_home:Location {id: "location_home"})
SET n_location_home.name = "Home in Cogne"
MERGE (n_weapon_copper_headed_masonry_hammer:Weapon {id: "weapon_copper_headed_masonry_hammer"})
SET n_weapon_copper_headed_masonry_hammer.name = "Copper-headed masonry hammer"
MERGE (n_evidence_blood:Evidence {id: "evidence_blood"})
SET n_evidence_blood.name = "Blood"
MERGE (n_evidence_bloody_footprints:Evidence {id: "evidence_bloody_footprints"})
SET n_evidence_bloody_footprints.name = "Bloody footprints"
MERGE (n_evidence_fingerprints:Evidence {id: "evidence_fingerprints"})
SET n_evidence_fingerprints.name = "Fingerprints"
MERGE (n_statement_annamaria_franzoni_innocence:Statement {id: "statement_annamaria_franzoni_innocence"})
SET n_statement_annamaria_franzoni_innocence.name = "Claims of innocence and unknown intruder"
MERGE (n_charge_voluntary_manslaughter:Charge {id: "charge_voluntary_manslaughter"})
SET n_charge_voluntary_manslaughter.name = "Voluntary manslaughter"

// --- RELAZIONI ---
MATCH (s {id: "person_samuele_lorenzi"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "person_annamaria_franzoni"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:IS_SUSPECTED_IN]->(t)
MATCH (s {id: "person_annamaria_franzoni"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_maria_carla_davieri"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:INVESTIGATES]->(t)
MATCH (s {id: "person_carlo_taormina"}), (t {id: "person_annamaria_franzoni"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_paola_savio"}), (t {id: "person_annamaria_franzoni"})
MERGE (s)-[:DEFENDS]->(t)
MATCH (s {id: "person_davide_lorenzi"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_ada_satragni"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "case_delitto_di_cogne"}), (t {id: "location_home"})
MERGE (s)-[:OCCURRED_AT]->(t)
MATCH (s {id: "location_home"}), (t {id: "location_cogne"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_cogne"}), (t {id: "location_aosta_valley"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "weapon_copper_headed_masonry_hammer"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:USED_IN]->(t)
MATCH (s {id: "evidence_blood"}), (t {id: "location_home"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_bloody_footprints"}), (t {id: "location_home"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "evidence_fingerprints"}), (t {id: "location_home"})
MERGE (s)-[:FOUND_AT]->(t)
MATCH (s {id: "person_annamaria_franzoni"}), (t {id: "statement_annamaria_franzoni_innocence"})
MERGE (s)-[:MADE_STATEMENT]->(t)
MATCH (s {id: "statement_annamaria_franzoni_innocence"}), (t {id: "case_delitto_di_cogne"})
MERGE (s)-[:RELATES_TO]->(t)
MATCH (s {id: "person_annamaria_franzoni"}), (t {id: "charge_voluntary_manslaughter"})
MERGE (s)-[:CHARGED_WITH]->(t)
MATCH (s {id: "case_delitto_di_cogne"}), (t {id: "charge_voluntary_manslaughter"})
MERGE (s)-[:INCLUDES_CHARGE]->(t)