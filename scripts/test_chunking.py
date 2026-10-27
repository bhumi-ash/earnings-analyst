
from analyst.chunking import parse_filename, chunk_text


# Test 1: Filename parsing
filename = "data/raw/INFOSYS_FY2025_annual-report.pdf"
metadata = parse_filename(filename)

print("Filename metadata:")
print(metadata)


# Test 2: Chunking
sample_text = (
    "Infosys revenue increased in FY2025. "
    "Operating profit also improved. "
    "The company continued investing in technology. "
) * 30

chunks = chunk_text(sample_text)

print("\nNumber of chunks:", len(chunks))
print("First chunk length:", len(chunks[0]))
print("First chunk preview:")
print(chunks[0][:300])
