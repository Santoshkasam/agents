from agents import Runner, trace, gen_trace_id
from research_agents import (
                             planner_agent, 
                             search_agent,
                             writer_agent,
                             email_sender_agent,
                             search_term,
                             ReportData,
                             research_assistant
                             )
import asyncio


class research_manager:

    async def run(self, query: str):
        trace_id = gen_trace_id()
        with trace("Research Manager Workflow", trace_id=trace_id):
            
            yield f"Starting research...; Trace: https://platform.openai.com/traces/trace?trace_id={trace_id}"
            
            yield f"Preparing follow-up questions"
            followup_message = await self.generate_followup_questions(query)
            followup_answer = yield followup_message
            
            yield f"Recieved answers to follow-up questions. Performing web searches"
            search_results = await self.run_searches(query, followup_message, followup_answer)
            
            yield f"Performed {len(search_results)} searches."
            yield "Writing report..."
            report         = await self.write_report(query, search_results)
            
            yield "Report written, now sending email..."
            await self.send_report_email(report)
            yield "Email sent, research complete!"
            
            yield report.markdown_report

    async def generate_followup_questions(self, query: str):
        """Generate three follow-up questions to clarify the requirements for the report"""
        result = await Runner.run(research_assistant, query)
        followup_questions = result.final_output.followups
        followup_message = "Please answer the following follow-up questions: \n\n"

        for i, question in enumerate(followup_questions, start=1):
            followup_message += f"{i}. " + question + "\n"

        return followup_message
    
    async def run_searches(self, query: str, follow_question: str, follow_answer: str):
        """ Plan the list of searches, and perform the searches """
        # Create search terms 
        print("Planning searches...")
        result = await Runner.run(planner_agent, f"Query: {query}")
        searches = result.final_output.search_terms
        
        # Perform searches
        print(f"Will perform {len(searches)} searches")
        tasks = [self.search(item) for item in searches]
        results = await asyncio.gather(*tasks)
        print("Finished searching")
        
        return results

    async def search(self, item: search_term):
        """ Perform a search for a given search term """
        input_message = f"Search term: {item.term}\nReason for search: {item.reason}"
        result = await Runner.run(search_agent, input_message)
        return result.final_output
    
    async def write_report(self,   query: str, search_results: list[str]):
        """ Write an executive style report with given search results """
        print("Writing the report...")
        input_message = f"User query: {query} \n\n {search_results}"
        result = await Runner.run(writer_agent, input_message)
        print("Finished writing report")
        return result.final_output

    async def send_report_email(self, report: ReportData):
        """ Given a report, send an email """
        print("Writing email...")
        result = await Runner.run(email_sender_agent, report.markdown_report)
        print("Email sent")
        return result.final_output