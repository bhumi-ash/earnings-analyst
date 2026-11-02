
import streamlit as st

from analyst.generation import answer_question
from analyst.retrieval import retrieve
from analyst.store import get_collection

st.set_page_config(page_title="Earnings Analyst", layout="wide")

st.title("Earnings & Annual Report Analyst")

st.caption(
    "Educational document-analysis tool, not investment advice. "
    "Answers come only from ingested reports. "
    "Always verify against the cited page."
)


@st.cache_data(ttl=60)
def load_options():
    metas = get_collection().get(include=["metadatas"])["metadatas"]

    return (
        sorted({m["company"] for m in metas}),
        sorted({m["fy"] for m in metas}),
        sorted({m["doc_type"] for m in metas}),
    )


companies, years, doc_types = load_options()

with st.sidebar:
    st.header("Filters")

    company = st.selectbox("Company", ["All"] + companies)
    fy = st.selectbox("Financial year", ["All"] + years)
    doc_type = st.selectbox("Document type", ["All"] + doc_types)

    k = st.slider("Passages to retrieve", 3, 12, 6)


question = st.text_input("Ask a question about the reports")

if st.button("Ask") and question.strip():
    try:
        with st.spinner("Searching and answering..."):
            hits = retrieve(
                question,
                k=k,
                company=None if company == "All" else company,
                fy=None if fy == "All" else fy,
                doc_type=None if doc_type == "All" else doc_type,
            )

        result = answer_question(question, hits)

    except Exception as exc:
        st.error(f"Something went wrong: {exc}")

    else:
        if result["found"]:
            st.subheader("Answer")
            st.write(result["answer"])
        else:
            st.warning(
                "Not found in the selected documents. " + result["answer"]
            )

        st.subheader("Sources")

        for s in result["sources"]:
            m = s["meta"]

            with st.expander(f"{m['source']}, page {m['page']}"):
                st.write(s["text"])
