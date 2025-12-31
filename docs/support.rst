

Support
=========

.. image:: /ML_Gekko_pics/gekko_support.png
   :width: 60%
   :align: center

Bugs
----

GEKKO is in its early stages and still under active development. If you identify a bug in the package, please submit an issue on `GitHub <https://github.com/BYU-PRISM/GEKKO>`_. 

If you would like to contribute to GEKKO development, please make pull requests on the `GitHub repo <https://github.com/BYU-PRISM/GEKKO>`_.

Questions
---------

Further clarification regarding GEKKO, please visit `Stack Overflow <https://stackoverflow.com/questions/tagged/gekko>`_ with questions tagged `gekko` for human-generated questions and answers. Generative AI is built into Gekko with the `support` module. Queries are sent to a web service and a text response is returned. The web service searches a list of hundreds of related `Gekko questions and answers <https://github.com/BYU-PRISM/GEKKO/blob/master/docs/llm/train.jsonl>`_ to add question context and receive a more relevant answer.

::

	from gekko import support
	a = support.agent()
	a.ask("Can you optimize the Rosenbrock function?")

Create a support agent with `support.agent()` and then ask any questions. Prior questions and answers are stored as context for follow-up questions. User questions are not stored for LLM training. The Gekko AI Assistant web service may be unavailable or slow down during periods of high use. 

A `local Gekko AI Assistant <https://apmonitor.com/dde/index.php/Main/RAGLargeLanguageModel>`_ can be run with Retrieval Augmented Generation (RAG) and choice of LLM on a local `ollama` server. Advanced Process Solutions, LLC (APS) is not responsible in any way for the Gekko AI Assistant accuracy, completeness, performance, timeliness, reliability, content, upgrades, or availability of any information and/or software received as a result of the use of the service. See APS `terms and conditions <https://apmonitor.com/wiki/index.php/Main/TermsConditions>`_.

Advanced Debugging
------------------

The files read/written by GEKKO are in the folder indicated in `m._path`. Information on debugging these files is available on `APMonitor <http://apmonitor.com/wiki/>`_.

Generative AI
------------------

Generative AI can also help with basic and advanced questions. Most Large Language Models (LLMs) have knowledge of the Gekko syntax and are able to help with generating prototype applications, suggesting performance improvements, answering questions that would be found in the documentation, designing applications, and working through errors. A context aware OpenAI GPT model is available for `Gekko GenAI Support <https://chat.openai.com/g/g-sl8WNWdO7-gekko-support>`_.

.. image:: /ML_Gekko_pics/gekko_gpt.png
   :width: 100%
   :align: center

