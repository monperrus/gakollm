import tiktoken
import sys

# Initialize the tokenizer and the model
tokenizer = tiktoken.encoding_for_model("gpt-35-turbo")
#model = Model()

if len(sys.argv)==1:
  text = "This is a sample text for OpenAI tokenization."
else:
  text = sys.argv[1]
# Tokenize the text
tokenized_text = tokenizer.encode(text)

print(tokenized_text)
# Print each token
for token in tokenized_text:
    print(tokenizer.decode_single_token_bytes(token).decode("utf8"))

# for token in range(0,128):
#   try:
#     print(token, tokenizer.decode_single_token_bytes(token).decode("utf8"))
#   except: pass
#     
