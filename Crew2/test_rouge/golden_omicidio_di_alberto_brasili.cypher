// --- NODI ---
MERGE (n_case_omicidio_di_alberto_brasili:Case {id: "case_omicidio_di_alberto_brasili"})
SET n_case_omicidio_di_alberto_brasili.name = "Omicidio di Alberto Brasili"
MERGE (n_person_alberto_brasili:Person {id: "person_alberto_brasili"})
SET n_person_alberto_brasili.name = "Alberto Brasili", n_person_alberto_brasili.role = "Victim", n_person_alberto_brasili.gender = "Male", n_person_alberto_brasili.profession = "commesso", n_person_alberto_brasili.is_deceased = true
MERGE (n_person_lucia_corna:Person {id: "person_lucia_corna"})
SET n_person_lucia_corna.name = "Lucia Corna", n_person_lucia_corna.role = "Witness", n_person_lucia_corna.gender = "Female", n_person_lucia_corna.is_deceased = false
MERGE (n_person_antonio_bega:Person {id: "person_antonio_bega"})
SET n_person_antonio_bega.name = "Antonio Bega", n_person_antonio_bega.role = "Suspect", n_person_antonio_bega.gender = "Male", n_person_antonio_bega.is_deceased = false
MERGE (n_person_pietro_croce:Person {id: "person_pietro_croce"})
SET n_person_pietro_croce.name = "Pietro Croce", n_person_pietro_croce.role = "Suspect", n_person_pietro_croce.gender = "Male", n_person_pietro_croce.is_deceased = false
MERGE (n_person_giorgio_nicolosi:Person {id: "person_giorgio_nicolosi"})
SET n_person_giorgio_nicolosi.name = "Giorgio Nicolosi", n_person_giorgio_nicolosi.role = "Suspect", n_person_giorgio_nicolosi.gender = "Male", n_person_giorgio_nicolosi.is_deceased = false
MERGE (n_person_enrico_caruso:Person {id: "person_enrico_caruso"})
SET n_person_enrico_caruso.name = "Enrico Caruso", n_person_enrico_caruso.role = "Suspect", n_person_enrico_caruso.gender = "Male", n_person_enrico_caruso.is_deceased = false
MERGE (n_person_giovanni_sciavicco:Person {id: "person_giovanni_sciavicco"})
SET n_person_giovanni_sciavicco.name = "Giovanni Sciavicco", n_person_giovanni_sciavicco.role = "Suspect", n_person_giovanni_sciavicco.gender = "Male", n_person_giovanni_sciavicco.is_deceased = false
MERGE (n_location_milano:Location {id: "location_milano"})
SET n_location_milano.name = "Milano"
MERGE (n_location_via_mascagni:Location {id: "location_via_mascagni"})
SET n_location_via_mascagni.name = "via Mascagni"
MERGE (n_location_piazza_san_babila:Location {id: "location_piazza_san_babila"})
SET n_location_piazza_san_babila.name = "piazza San Babila"
MERGE (n_location_ospedale_fatebenefratelli:Location {id: "location_ospedale_fatebenefratelli"})
SET n_location_ospedale_fatebenefratelli.name = "ospedale Fatebenefratelli"

// --- RELAZIONI ---
MATCH (s {id: "person_alberto_brasili"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:IS_VICTIM_OF]->(t)
MATCH (s {id: "person_lucia_corna"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:INVOLVED_IN]->(t)
MATCH (s {id: "person_antonio_bega"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_pietro_croce"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_giorgio_nicolosi"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_enrico_caruso"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "person_giovanni_sciavicco"}), (t {id: "case_omicidio_di_alberto_brasili"})
MERGE (s)-[:COMMITTED]->(t)
MATCH (s {id: "case_omicidio_di_alberto_brasili"}), (t {id: "location_milano"})
MERGE (s)-[:OCCURRED_AT]->(t)
MATCH (s {id: "location_via_mascagni"}), (t {id: "location_milano"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_piazza_san_babila"}), (t {id: "location_milano"})
MERGE (s)-[:WITHIN]->(t)
MATCH (s {id: "location_ospedale_fatebenefratelli"}), (t {id: "location_milano"})
MERGE (s)-[:WITHIN]->(t)