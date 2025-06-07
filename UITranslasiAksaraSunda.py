import streamlit as st
import requests

FUSEKI_ENDPOINT = "http://localhost:3030/semweb-translasi-aksara-sunda-dataset-v1/query"

st.set_page_config(page_title="Kamus Aksara Sunda", layout="centered")
st.title("Kamus Aksara Sunda")

selected_kata = st.query_params.get("kata", None)

def search_kata(keyword):
    query = f"""
    PREFIX : <http://example.org/ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT DISTINCT ?aksara WHERE {{
        ?kata a :KataNaskah ;
              rdf:value ?aksara .
        FILTER(CONTAINS(LCASE(STR(?aksara)), LCASE("{keyword}")))
    }}
    ORDER BY ?aksara
    """
    response = requests.post(
        FUSEKI_ENDPOINT,
        headers={"Content-Type": "application/sparql-query", "Accept": "application/sparql-results+json"},
        data=query.encode("utf-8")
    )
    if response.status_code == 200:
        return [r["aksara"]["value"] for r in response.json()["results"]["bindings"]]
    else:
        st.error("Gagal mengambil data dari endpoint SPARQL.")
        return []

def get_terjemahan(kata):
    query = f"""
    PREFIX : <http://example.org/ontology#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>

    SELECT ?terjemahan WHERE {{
        ?kata a :KataNaskah ;
              rdf:value "{kata}"@su ;
              :hasTranslation ?terjemahankata .
        ?terjemahankata rdf:value ?terjemahan .
    }}
    """
    response = requests.post(
        FUSEKI_ENDPOINT,
        headers={"Content-Type": "application/sparql-query", "Accept": "application/sparql-results+json"},
        data=query.encode("utf-8")
    )
    if response.status_code == 200:
        return [r["terjemahan"]["value"] for r in response.json()["results"]["bindings"]]
    else:
        st.error("Gagal mengambil terjemahan.")
        return []

if selected_kata == None:
    kata_input = st.text_input("Masukkan Kata Latin Aksara Sunda :", "")
    if kata_input:
        hasil_kata = search_kata(kata_input)
        if hasil_kata:
            st.write("Hasil pencarian :")
            for i, kata in enumerate(hasil_kata):
                st.link_button(
                    label=f"{kata}",
                    url=f"?kata={kata}"
                )
        else:
            st.write("Hasil pencarian :")
            st.warning("Kata Tidak Ditemukan")
else:
    st.markdown(f"## Aksara: `{selected_kata}`")
    terjemahan = get_terjemahan(selected_kata)
    if terjemahan:
        st.markdown(f"## Terjemahan: ")
        for t in terjemahan:
            st.markdown(f"#### {t}")
    else:
        st.markdown(f"## Terjemahan: ")
        st.warning("Tidak Ditemukan Terjemahan")

    st.markdown("---")
    st.markdown("[Kembali ke pencarian](./)")