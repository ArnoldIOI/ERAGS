import time
from llama_index.core import StorageContext, load_index_from_storage
from llama_index.core import SimpleDirectoryReader, VectorStoreIndex
from llama_index.core.storage.chat_store import SimpleChatStore
from llama_index.core.memory import ChatMemoryBuffer
from rdf_logging import log_chat_session, log_solution


class RAGApplication:
    def __init__(self):
        self.template = (
            "We have provided context information below. \n"
            "---------------------\n"
            "{context_str}"
            "\n---------------------\n"
            "Given this information, please answer the question: {query_str}\n"
        )
        self.logs = {"rounds": []}

    def set_up(self, load=False):
        chat_store = SimpleChatStore()
        session_token = str(int(time.time()))
        self.chat_memory = ChatMemoryBuffer.from_defaults(
            token_limit=3000,
            chat_store=chat_store,
            chat_store_key=session_token,
        )
        if load:
            # rebuild storage context
            storage_context = StorageContext.from_defaults(persist_dir="../data/index/")
            # load index
            self.index = load_index_from_storage(storage_context)
        else:
            # Load data
            reader = SimpleDirectoryReader(input_dir="../data/knowledge_base/")
            documents = reader.load_data()
            # Index data
            self.index = VectorStoreIndex.from_documents(documents)
            # Store index
            self.index.storage_context.persist("../data/index/")

    def chat(self, query):
        round_log = {}
        self.logs["rounds"].append(round_log)
        round_log["generator"] = "DefaultGenerator"
        retriever = self.index.as_query_engine()
        round_log["retriever"] = "DefaultRetriever"
        round_log["knowledge_base"] = "DefaultKnowledgeBase"
        round_log["query"] = query
        response = retriever.query(query)
        round_log["retrieved_info"] = response
        prompt = self.template.format(context_str=response, query_str=query)
        round_log["prompt"] = prompt
        res = self.index.as_chat_engine(memory=self.chat_memory).chat(prompt)
        round_log["response"] = res.response
        return res.response

    def chat_loop(self):
        self.logs["chat_session_id"] = self.chat_memory.chat_store_key
        while True:
            query = input("Enter your query: ")
            if query == "exit":
                break
            res = self.chat(query)
            print(res)


if __name__ == '__main__':
    from dotenv import load_dotenv
    load_dotenv()
    print("Welcome to RAG-based Education System!")
    student = input("Please enter your student ID:")
    print("Student ID: ", student)
    solution = ""
    chat_sessions = []
    while True:
        # option: 1->chat; 2->compose solution; 3->exit
        option = input("Enter option(1: chat; 2: compose solution; 3: exit): ")
        if option == "1":
            rag = RAGApplication()
            rag.set_up(load=True)
            rag.chat_loop()
            rag.logs["student_id"] = student
            log_chat_session(rag.logs)
            chat_sessions.append(rag.logs["chat_session_id"])
        elif option == "2":
            solution = input("Compose solution: ")
        elif option == "3":
            break
        else:
            print("Invalid option. Please enter again.")

    print("Solution: ", solution)
    random_solution_id = str(int(time.time()))
    log_solution(random_solution_id, solution, chat_sessions)
    print("Solution ID: ", random_solution_id)
