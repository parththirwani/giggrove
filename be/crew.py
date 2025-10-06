
from agents import CompanyResearchAgents
from tasks import CompanyResearchTasks
from jobs_manager import append_event
from crewai import Crew

class CompanyResearchCrew: 
    def __init__(self, job_id):
        self.job_id = job_id
        self.crew = None
    
    def setup_crew (self, companies: list[str], positions: list[str]):
        print(
            f"Setting up crew for {self.job_id} with companies{companies} and postions {positions}"
        )
            #SETUP AGENTS
        agents = CompanyResearchAgents()
        research_manager = agents.research_manager(companies, positions)
        company_research_agent = agents.company_research_agent()

        #SETUP TASKS
        tasks = CompanyResearchTasks(self.job_id)
        company_research_task = [
            tasks.company_research(company_research_agent, company, positions) for company in companies
        ]

        manage_research = tasks.manage_research(research_manager, companies, positions, company_research_task)

        #CREATE CRERW
        self.crew = Crew(
            agents=[research_manager, company_research_agent],
            tasks= [*company_research_task, manage_research],
            verbose=True
        )

    
    def kickoff(self): 
        if not self.crew:
            print(
                f"Something went wrong. No Crew found for {self.job_id}"
            )
            return
        
        append_event(self.job_id, "CREW STARTED")
        
        try:
            print(f"Running crew for {self.job_id}")
            results = self.crew.kickoff()
            append_event(self.job_id, "CREW COMPLETED")
            return results
        
        except Exception as e:
            append_event(self.job_id, f"CREW FAILED{str(e)}")
            print(str(e))
        
