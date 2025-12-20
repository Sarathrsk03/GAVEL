from agents.precedent_searcher.agent import case_breakdown_agent, precedent_searcher_agent, precedent_verifier_agent

class PrecedentSearchState:
    def __init__(self, user_input):
        self.user_input = user_input
        self.structured_facts = None
        self.search_queries = None
        self.search_results = None
        self.verified_precedents = None
        self.final_memo = None

class PrecedentSearchRunner:
    def __init__(self, state):
        self.state = state
        self.case_breakdown_agent = case_breakdown_agent
        self.precedent_searcher_agent = precedent_searcher_agent
        self.precedent_verifier_agent = precedent_verifier_agent

    def run_case_breakdown(self):
        self.state.structured_facts = self.case_breakdown_agent.run(self.state.user_input)
        return self.state.structured_facts

    def run_precedent_search(self):
        if not self.state.structured_facts:
            self.run_case_breakdown()
        self.state.search_results = self.precedent_searcher_agent.run(self.state.structured_facts)
        return self.state.search_results

    def run_precedent_verification(self):
        if not self.state.search_results:
            self.run_precedent_search()
        self.state.final_memo = self.precedent_verifier_agent.run(self.state.search_results)
        return self.state.final_memo

    def run_full_search(self):
        self.run_case_breakdown()
        self.run_precedent_search()
        self.run_precedent_verification()
        return self.state.final_memo
