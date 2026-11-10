
import streamlit as st

from analyst.generation import answer_labelled, answer_question
from analyst.hybrid import retrieve_bm25
from analyst.query_rewriting import rewrite_query
from analyst.store import get_collection


st.set_page_config(
    page_title="Earnings Analyst",
    layout="wide"
)

st.title("Earnings & Annual Report Analyst")

st.caption(
    "Educational document-analysis tool, not investment advice. "
    "Answers come only from ingested reports. "
    "Always verify against the cited page."
)


@st.cache_data(ttl=60)
def load_options():
    metas = get_collection().get(
        include=["metadatas"]
    )["metadatas"]

    return (
        sorted({m["company"] for m in metas}),
        sorted({m["fy"] for m in metas}),
        sorted({m["doc_type"] for m in metas}),
    )


companies, years, doc_types = load_options()


with st.sidebar:
    st.header("Filters")

    company = st.selectbox(
        "Company",
        ["All"] + companies
    )

    fy = st.selectbox(
        "Financial year",
        ["All"] + years
    )

    doc_type = st.selectbox(
        "Document type",
        ["All"] + doc_types
    )

    k = st.slider(
        "Passages to retrieve",
        3,
        12,
        10
    )

    labelled = st.checkbox(
        "Labelled answer (facts / management claims / interpretation)"
    )


question = st.text_input(
    "Ask a question about the reports"
)


if st.button("Ask") and question.strip():

    try:
        with st.spinner(
            "Rewriting question, searching reports and generating answer..."
        ):

            # Step 1: Rewrite the original question
            rewritten_question = rewrite_query(question)

            # Step 2: Retrieve passages using rewritten BM25
            hits = retrieve_bm25(
                rewritten_question,
                k=k,
                company=None if company == "All" else company,
                fy=None if fy == "All" else fy,
                doc_type=None if doc_type == "All" else doc_type,
            )

            # Step 3: Generate the selected answer format
            if labelled:
                result = answer_labelled(question, hits)
            else:
                result = answer_question(question, hits)

        # Display the rewritten query
        with st.expander("View rewritten search query"):
            st.write(rewritten_question)

        # Display the answer
        if labelled and result["found"]:

            for title, key in [
                ("Reported facts", "reported_facts"),
                ("Management claims", "management_claims"),
                (
                    "Interpretation (the model's reading; verify)",
                    "interpretation"
                ),
            ]:
                st.subheader(title)

                if result[key]:
                    for item in result[key]:
                        st.write("- " + item["text"])
                else:
                    st.info("No statements in this category.")

        elif result["found"]:
            st.subheader("Answer")
            st.write(result["answer"])

        else:
            st.warning(
                "Not found in the selected documents. "
                + result["answer"]
            )

        # Display sources
        st.subheader("Sources")

        if result["sources"]:
            for source in result["sources"]:
                meta = source["meta"]

                with st.expander(
                    f"{meta['source']}, page {meta['page']}"
                ):
                    st.write(source["text"])
        else:
            st.info("No source passages were cited.")

    except Exception as exc:
        st.error(f"Something went wrong: {exc}")
