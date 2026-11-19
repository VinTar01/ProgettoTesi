from crewai import Crew, Process
from Crew4.agents_crew4 import agente_esploratore
from Crew4.tasks_crew4 import task_risposta_domanda

crew_esploratore_grafo = Crew(
    agents=[agente_esploratore],
    tasks=[task_risposta_domanda],
    process=Process.sequential,
    verbose=True
)