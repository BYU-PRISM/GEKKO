class agent:
    '''
    This class provides an interface for sending questions to a WebSocket server 
    and receiving streamed answers. It maintains a context of previous Q&A pairs to provide 
    context for new questions.

    Attributes:
        context (list): A list of tuples containing past questions and answers.
        context_size (int): The maximum number of Q&A pairs to keep in the context.
                            Reduce context_size if there is a server time-out.

    Methods:
        is_notebook(): Check if the runtime environment is a Jupyter notebook.
        _msg(uri, q, nb): Send a question to the WebSocket server and stream the response.
        _build_context(new_q): Build a context string for the current question.
        ask(q): Send a question and update the context with the answer.
        history(): Return the current context of Q&A pairs.
    '''
    def __init__(self, context_size=3):
        '''
        Initializes the agent with a specified context size.

        Args:
            context_size (int): The number of Q&A pairs to store in the context. Default is 3.
        '''
        self.context = []
        self.context_size = context_size

    @staticmethod
    def is_notebook():
        '''
        Check if the current environment is a Jupyter notebook.

        Returns:
            bool: True if in a Jupyter notebook, False otherwise.
        '''
        try:
            from IPython import get_ipython
            if 'IPKernelApp' not in get_ipython().config:
                return False
        except Exception:
            return False
        return True

    @staticmethod
    async def _msg(uri, q, nb):
        """
        Send a question to the WebSocket server and stream the response.
        """
        try:
            import websockets
        except ImportError:
            print("Error: Install websockets with 'pip install websockets'")
            return

        async def stream_response(websocket):
            full_answer = ''
            if nb:
                from IPython.display import display, Markdown, update_display
                # Create a persistent display area using a unique display_id.
                md_display_id = "streaming_answer"
                display(Markdown(""), display_id=md_display_id)
                async for chunk in websocket:
                    full_answer += chunk
                    update_display(Markdown(full_answer), display_id=md_display_id)
            else:
                async for chunk in websocket:
                    full_answer += chunk
                    print(chunk, end='', flush=True)
            return full_answer

        try:
            async with websockets.connect(uri) as websocket:
                await websocket.send(q)
                answer = await stream_response(websocket)
                return answer
        except Exception:
            import ssl
            ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            async with websockets.connect(uri, ssl=ssl_context) as websocket:
                await websocket.send(q)
                answer = await stream_response(websocket)
                return answer

    def _build_context(self, new_q):
        '''
        Build context from prior questions and answers.

        Args:
            new_q (str): The new question to be sent.

        Returns:
            context_str: The question and answer pairs according to context_size with
                         the new question at the end.
        '''
        context_str = ""
        if len(self.context) <= self.context_size:
            # use all Q+A pairs if less than or equal to context_size
            cnxt = self.context
        else:
            # only use the last context_size pairs
            cnxt = self.context[-self.context_size:]
        for q, a in cnxt:
            context_str += f"### Prior Question for Context: {q} ### Prior Answer for Context: {a}\n\n"
        context_str += f"### New Question: {new_q}"
        return context_str

    def ask(self, q):
        '''
        Send a question to the WebSocket server and update the context with the answer.

        Args:
            q (str): The question to be sent.

        Returns:
            answer (str): The full streamed answer received from the server if not in a 
                          Jupyter notebook. In a notebook, the answer is displayed live.
        '''
        import asyncio
        nb = agent.is_notebook()
        uri = "wss://hedengren.net/gekko"

        full_q = self._build_context(q)

        answer = None
        if nb:
            # Use the existing event loop in the notebook environment
            import nest_asyncio
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            answer = loop.run_until_complete(agent._msg(uri, full_q, nb))
        else:
            # Use a new event loop in a standard Python environment
            answer = asyncio.run(agent._msg(uri, full_q, nb))

        # Update context with the most recent question and answer
        self.context.append((q, answer))
        
        if nb:
            return
        else:
            return answer

    def history(self):
        '''
        Return the current context of Q&A pairs.

        Returns:
            list: A list of tuples with past questions and answers.
        '''
        return self.context
