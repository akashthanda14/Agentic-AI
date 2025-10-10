import tiktoken;

enc = tiktoken.encoding_for_model("gpt-4o")

text = "Hey Akash thsi is akashdeep"

tokens = enc.encode(text)
# Tokens [25216, 13232, 1229, 325, 4778, 382, 2946, 1229, 71028]

print("Tokens",tokens)

decoded = enc.decode([25216, 13232, 1229, 325, 4778, 382, 2946, 1229, 71028])

print("Decoded",decoded)