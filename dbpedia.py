from SPARQLWrapper import SPARQLWrapper, JSON

sparql = SPARQLWrapper("http://dbpedia.org/sparql")

sparql.setQuery("""
    PREFIX dbpedia-owl: <http://dbpedia.org/ontology/>
    PREFIX ec: <https://github.com/tibonto/educor#>
    PREFIX dc: <http://purl.org/dcx/lrmi-vocabs/alignmentType/>
    SELECT ?label
    WHERE { <http://dbpedia.org/resource/Asturias>
                ec:consistsOfKnowledge ?label
    }
""")
sparql.setReturnFormat(JSON)
results = sparql.query()
results.print_results()