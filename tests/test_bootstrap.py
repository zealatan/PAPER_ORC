"""Step 00 sanity check: every module can be imported without error."""


def test_import_models():
    import papernav.models


def test_import_parser():
    import papernav.parser


def test_import_pipeline():
    import papernav.pipeline


def test_import_report_writer():
    import papernav.report_writer


def test_import_citation_extractor():
    import papernav.citation.extractor


def test_import_citation_bibliography():
    import papernav.citation.bibliography


def test_import_citation_classifier():
    import papernav.citation.classifier


def test_import_graph_history_tree():
    import papernav.graph.history_tree


def test_import_graph_baseline_graph():
    import papernav.graph.baseline_graph


def test_import_graph_visualizer():
    import papernav.graph.visualizer


def test_import_agents_topic_relevance():
    import papernav.agents.topic_relevance


def test_import_agents_citation_value():
    import papernav.agents.citation_value


def test_import_agents_experiment_value():
    import papernav.agents.experiment_value


def test_import_agents_strategic_value():
    import papernav.agents.strategic_value


def test_import_agents_weakness_risk():
    import papernav.agents.weakness_risk


def test_import_agents_final_judge():
    import papernav.agents.final_judge
