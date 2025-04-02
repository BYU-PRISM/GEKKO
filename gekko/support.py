import uuid

class agent:
    '''
    This class provides an interface for sending questions to a WebSocket server 
    and receiving streamed answers. It maintains a context of previous Q&A pairs to provide 
    context for new questions.

    Attributes:
        context (list): A list of tuples containing past questions and answers.
        context_size (int): The maximum number of Q&A pairs to keep in the context.
                            Reduce context_size if there is a server time-out.
    '''
    # Class-level variables for IPython display functions (initialized once)
    _ipython_initialized = False
    _ipython_display = None
    _ipython_Markdown = None
    _ipython_update_display = None

    def __init__(self, context_size=3):
        '''
        Initializes the agent with a specified context size and, if in a notebook,
        imports IPython display functions once.
        
        Args:
            context_size (int): The number of Q&A pairs to store in the context. Default is 3.
        '''
        self.context = []
        self.context_size = context_size
        self.nb = agent.is_notebook()
        if self.nb and not agent._ipython_initialized:
            try:
                from IPython.display import display, Markdown, update_display
                agent._ipython_display = display
                agent._ipython_Markdown = Markdown
                agent._ipython_update_display = update_display
                agent._ipython_initialized = True
            except Exception:
                # If for some reason the import fails, treat as not in notebook mode.
                self.nb = False

    @staticmethod
    def is_notebook():
        '''
        Check if the current environment is a Jupyter notebook. Also attempts to import 
        IPython display functions.
        
        Returns:
            bool: True if in a Jupyter notebook with IPython display available, False otherwise.
        '''
        try:
            from IPython import get_ipython
            if 'IPKernelApp' not in get_ipython().config:
                return False
            # The following imports are attempted here but are stored in __init__
            from IPython.display import display, Markdown, update_display
        except Exception:
            return False
        return True

    @staticmethod
    async def _msg(uri, q, nb):
        '''
        Send a question to the WebSocket server and stream the response.
        
        Args:
            uri (str): The WebSocket server URI.
            q (str): The question (with context) to be sent.
            nb (bool): True if running in a Jupyter notebook.
        
        Returns:
            str: The complete answer (concatenated from all chunks) after the stream ends.
        '''
        try:
            import websockets
        except ImportError:
            print("Error: Install websockets with 'pip install websockets'")
            return

        async def stream_response(websocket):
            full_answer = ''
            if nb:
                # Create a unique display ID for this streamed answer
                display_id = str(uuid.uuid4())
                # Initialize the persistent display area with the unique display_id
                agent._ipython_display(agent._ipython_Markdown(""), display_id=display_id)
                async for chunk in websocket:
                    full_answer += chunk
                    # Update the same display area with the new concatenated text
                    agent._ipython_update_display(agent._ipython_Markdown(full_answer), display_id=display_id)
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
            str: The context string composed of previous Q&A pairs plus the new question.
        '''
        context_str = ""
        if len(self.context) <= self.context_size:
            cnxt = self.context
        else:
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
            str or None: The full streamed answer if not in a notebook; otherwise, the answer 
                         is displayed live.
        '''
        import asyncio
        nb = self.nb
        uri = "wss://hedengren.net/gekko"

        full_q = self._build_context(q)

        if nb:
            import nest_asyncio
            nest_asyncio.apply()
            loop = asyncio.get_event_loop()
            answer = loop.run_until_complete(agent._msg(uri, full_q, nb))
        else:
            answer = asyncio.run(agent._msg(uri, full_q, nb))

        self.context.append((q, answer))
        return None if nb else answer

    def history(self):
        '''
        Return the current context of Q&A pairs.
        
        Returns:
            list: A list of tuples with past questions and answers.
        '''
        return self.context
