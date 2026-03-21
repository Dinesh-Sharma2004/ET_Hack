import networkx as nx

from app.schemas.common import Article
from app.schemas.story import StoryArcResponse, StoryEdge, StoryNode, TimelinePoint


class StoryGraphEngine:
    def build(self, articles: list[Article]) -> StoryArcResponse:
        graph = nx.Graph()
        for article in articles:
            for entity in article.entities:
                graph.add_node(entity, group="company" if entity.isupper() else "theme")
            for source in article.entities:
                for target in article.entities:
                    if source != target:
                        graph.add_edge(source, target, relation="co-mentioned")

        timeline = [
            TimelinePoint(
                date=article.published_at,
                headline=article.title,
                sentiment=article.sentiment,
                impact_score=round(abs(article.sentiment) * 50 + len(article.entities) * 8, 1),
            )
            for article in articles[:5]
        ]
        nodes = [StoryNode(id=node, label=node, group=graph.nodes[node]["group"]) for node in graph.nodes]
        edges = [
            StoryEdge(source=edge[0], target=edge[1], relation=graph.edges[edge]["relation"]) for edge in graph.edges
        ]
        return StoryArcResponse(
            theme="AI Capex and India Growth Repricing",
            timeline=timeline,
            entities=nodes,
            relationships=edges,
            what_next=[
                "Expect management commentary to shift from experimentation to measurable ROI on AI spend.",
                "Policy continuity could strengthen domestic manufacturing and digital infra beneficiaries.",
                "If global growth softens, selective quality names may outperform broad thematic baskets.",
            ],
        )
