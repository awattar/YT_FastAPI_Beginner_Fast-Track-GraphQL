from starlette.responses import HTMLResponse
from starlette.requests import Request


def make_custom_graphiql_handler():
    """
    Custom GraphiQL handler that uses reliable CDN URLs.
    Replaces the broken make_graphiql_handler from starlette-graphene3.
    """

    graphiql_html = """
<!DOCTYPE html>
<html>
<head>
    <title>GraphiQL</title>
    <style>
        html, body {
            height: 100%;
            margin: 0;
            overflow: hidden;
            width: 100%;
        }
        #graphiql {
            height: 100vh;
        }
    </style>
    <!-- GraphiQL CSS from jsDelivr (more reliable than unpkg) -->
    <link href="https://cdn.jsdelivr.net/npm/graphiql@3.7.1/graphiql.min.css" rel="stylesheet" />
    
    <!-- React dependencies -->
    <script src="https://cdn.jsdelivr.net/npm/react@18.3.1/umd/react.production.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/react-dom@18.3.1/umd/react-dom.production.min.js"></script>
    
    <!-- GraphiQL -->
    <script src="https://cdn.jsdelivr.net/npm/graphiql@3.7.1/graphiql.min.js"></script>
</head>
<body>
    <div id="graphiql">Loading GraphiQL...</div>
    
    <script>
        // Configure GraphQL endpoint
        const graphQLFetcher = (graphQLParams) => {
            return fetch(window.location.pathname, {
                method: 'POST',
                headers: {
                    'Accept': 'application/json',
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(graphQLParams),
                credentials: 'include',
            }).then(response => response.json());
        };

        // Render GraphiQL
        const root = ReactDOM.createRoot(document.getElementById('graphiql'));
        root.render(React.createElement(GraphiQL, {
            fetcher: graphQLFetcher,
            defaultEditorToolsVisibility: true,
        }));
    </script>
</body>
</html>
    """

    async def graphiql_handler(request: Request):
        return HTMLResponse(graphiql_html)

    return graphiql_handler
