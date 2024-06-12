import os

from rdflib import Graph, Literal, RDF, Namespace, PROV

from utils.utils import insert_data_to_graphdb

g = Graph()


def log_chat_session(logs):
    RAG = Namespace("http://example.org/rag-based-edu-ontology#")
    PP = Namespace("http://purl.org/net/p-plan#")

    # ChatSession
    chat_session = RAG[f"ChatSession{logs['chat_session_id']}"]
    g.add((chat_session, RDF.type, RAG.ChatSession))
    g.add((chat_session, RAG.id, Literal(logs['chat_session_id'])))
    student = RAG[f"Student{logs['student_id']}"]
    g.add((student, RAG.id, Literal(logs['student_id'])))
    g.add((chat_session, RAG.ChatSessionStartedByStudent, student))

    for i, round_log in enumerate(logs['rounds']):
        round = RAG[f"Session{logs['chat_session_id']}Round{i}"]
        roundplan = RAG[f"Session{logs['chat_session_id']}Round{i}Plan"]
        g.add((round, RDF.type, RAG.Round))
        g.add((round, PP.isDecomposedAsPlan, roundplan))
        g.add((round, PP.isStepOfPlan, chat_session))
        g.add((roundplan, RDF.type, PP.Plan))
        g.add((roundplan, PP.isSubPlanOfPlan, chat_session))

        retriever = RAG[f"DefaultRetriever"]
        g.add((retriever, RDF.type, RAG.Retriever))
        g.add((retriever, RAG.retrieverModelVersion, Literal(round_log['retriever'])))
        knowledge_base = RAG[f"DefaultKnowledgeBase"]
        g.add((knowledge_base, RDF.type, RAG.KnowledgeBase))
        g.add((knowledge_base, RAG.KnowledgeBaseVersion, Literal(round_log['knowledge_base'])))
        retrieval = RAG[f"Session{logs['chat_session_id']}Round{i}Retrieval"]
        query = RAG[f"Session{logs['chat_session_id']}Round{i}Query"]
        retrieved_info = RAG[f"Session{logs['chat_session_id']}Round{i}RetrievedInfo"]
        g.add((retrieval, RDF.type, RAG.Retrieval))
        g.add((retrieval, PP.isStepOfPlan, roundplan))
        g.add((query, RDF.type, RAG.Query))
        g.add((query, RAG.queryContent, Literal(round_log['query'])))
        g.add((retrieved_info, RDF.type, RAG.RetrievedInformation))
        g.add((retrieved_info, RAG.RetrievedContent, Literal(round_log['retrieved_info'])))
        g.add((retrieval, PROV.used, Literal(round_log['retriever'])))
        g.add((retrieval, PROV.used, Literal(round_log['knowledge_base'])))
        g.add((retrieval, PP.hasInputVar, query))
        g.add((retrieval, PP.hasOutputVar, retrieved_info))

        generator = RAG[f"DefaultGenerator"]
        g.add((generator, RDF.type, RAG.Generator))
        g.add((generator, RAG.GeneratorModelVersion, Literal(round_log['generator'])))
        generation = RAG[f"Session{logs['chat_session_id']}Round{i}Generation"]
        g.add((generation, RDF.type, RAG.Generation))
        g.add((generation, PP.isStepOfPlan, roundplan))
        g.add((generation, PROV.used, generator))
        g.add((generation, PROV.used, query))
        g.add((generation, PROV.used, retrieved_info))
        prompt = RAG[f"Session{logs['chat_session_id']}Round{i}Prompt"]
        g.add((prompt, RDF.type, RAG.Prompt))
        g.add((prompt, RAG.promptContent, Literal(round_log['prompt'])))
        response = RAG[f"Session{logs['chat_session_id']}Round{i}Response"]
        g.add((response, RDF.type, RAG.Response))
        g.add((response, RAG.responseContent, Literal(round_log['response'])))
        g.add((generation, PP.hasInputVar, prompt))
        g.add((generation, PP.hasOutputVar, response))

    # g.serialize("data/rdf/chat_session.ttl", format="turtle")


def log_solution(solution_id, solution_content, chat_sessions):
    RAG = Namespace("http://example.org/rag-based-edu-ontology#")

    solution = RAG[f"Solution{solution_id}"]
    g.add((solution, RDF.type, RAG.StudentSolution))
    for chat_session_id in chat_sessions:
        chat_session = RAG[f"ChatSession{chat_session_id}"]
        g.add((solution, RAG.BasedOnChatSession, chat_session))
    g.add((solution, RAG.solutionContent, Literal(solution_content)))
    g.add((solution, RAG.id, Literal(solution_id)))
    g.serialize(f"../data/rdf/log{solution_id}.ttl", format="turtle")

    from dotenv import load_dotenv

    # Load environment variables from .env file
    load_dotenv()

    # Fetching from environment variables
    graphdb_url = os.getenv('GRAPHDB_URL')
    username = os.getenv('GRAPHDB_USERNAME')
    password = os.getenv('GRAPHDB_PASSWORD')

    insert_data_to_graphdb(g, graphdb_url, username, password)

