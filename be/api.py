import json
from threading import Thread
import uuid
from datetime import datetime
from flask import Flask, abort, jsonify, request
from jobs_manager import Event, append_event, jobs_lock, jobs
from crew import CompanyResearchCrew

app = Flask(__name__)

def kickoff_crew(job_id: str, companies: list[str], positions: list[str]):
    print(f"Running crew job for {job_id} with companies {companies} for positions {positions}")
    results = None
    try:
        company_research_crew = CompanyResearchCrew(job_id)
        company_research_crew.setup_crew(companies, positions)
        results = company_research_crew.kickoff()
    except Exception as e:
        print(f"Crew job failed : {str(e)}")
        append_event(job_id, f"CREW FAILED: {str(e)}")
        with jobs_lock:
            jobs[job_id].status = "ERROR"
            jobs[job_id].result = str(e)

    with jobs_lock:
        jobs[job_id].status = "COMPLETE"
        jobs[job_id].result = results
        jobs[job_id].events.append(
            Event(
                timestamp=datetime.now(),
                data="CREW COMPLETED"
            )
        )

@app.route('/api/crew', methods=['POST'])
def run_crew():
    data = request.json
    if not data or 'companies' not in data or 'positions' not in data:
        abort(400, description="Invalid input data provided.")

    job_id = str(uuid.uuid4())
    companies = data['companies']
    positions = data['positions']

    thread = Thread(target=kickoff_crew, args=(job_id, companies, positions))
    thread.start()

    return jsonify({"job_id": job_id}), 202

@app.route("/api/crew/<job_id>", methods=['GET'])
def get_status(job_id):
    with jobs_lock:
        job = jobs.get(job_id)  # Fix: was job.get(job_id)
        if not job:
            abort(404)

    try:
        result_json = json.loads(job.result)
    except:
        result_json = job.result

    return jsonify({
        "job_id": job_id,
        "status": job.status,
        "result": result_json,
        "events": [{"timestamp": event.timestamp.isoformat(), "data": event.data} for event in job.events]
    }), 200

if __name__ == "__main__":
    app.run(debug=True, port=3000)
