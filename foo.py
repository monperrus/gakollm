Traceback (most recent call last):
  File "/home/martin/martin-no-backup/chatgpt-cli/./comment-file-with-llm.py", line 141, in <module>
    answer = extract_program(get_llm_answer(prompt))
                             ^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/martin-no-backup/chatgpt-cli/./comment-file-with-llm.py", line 26, in get_llm_answer
    return get_gpt3_answer(prompt)
           ^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/martin-no-backup/chatgpt-cli/./comment-file-with-llm.py", line 104, in get_gpt3_answer
    response = client.chat.completions.create(#model="gpt-3.5-turbo",
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/openai/_utils/_utils.py", line 277, in wrapper
    return func(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/openai/resources/chat/completions.py", line 590, in create
    return self._post(
           ^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/openai/_base_client.py", line 1240, in post
    return cast(ResponseT, self.request(cast_to, opts, stream=stream, stream_cls=stream_cls))
                           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/openai/_base_client.py", line 921, in request
    return self._request(
           ^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/openai/_base_client.py", line 952, in _request
    response = self._client.send(
               ^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpx/_client.py", line 914, in send
    response = self._send_handling_auth(
               ^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpx/_client.py", line 942, in _send_handling_auth
    response = self._send_handling_redirects(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpx/_client.py", line 979, in _send_handling_redirects
    response = self._send_single_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpx/_client.py", line 1015, in _send_single_request
    response = transport.handle_request(request)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpx/_transports/default.py", line 233, in handle_request
    resp = self._pool.handle_request(req)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/connection_pool.py", line 216, in handle_request
    raise exc from None
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/connection_pool.py", line 196, in handle_request
    response = connection.handle_request(
               ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/connection.py", line 101, in handle_request
    return self._connection.handle_request(request)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/http11.py", line 143, in handle_request
    raise exc
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/http11.py", line 113, in handle_request
    ) = self._receive_response_headers(**kwargs)
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/http11.py", line 186, in _receive_response_headers
    event = self._receive_event(timeout=timeout)
            ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_sync/http11.py", line 224, in _receive_event
    data = self._network_stream.read(
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/martin/.local/lib/python3.11/site-packages/httpcore/_backends/sync.py", line 126, in read
    return self._sock.recv(max_bytes)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/ssl.py", line 1296, in recv
    return self.read(buflen)
           ^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.11/ssl.py", line 1169, in read
    return self._sslobj.read(len)
           ^^^^^^^^^^^^^^^^^^^^^^
KeyboardInterrupt
