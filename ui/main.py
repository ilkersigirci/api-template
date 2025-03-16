from fasthtml.common import Div, P, fast_app

app, rt = fast_app()


@rt("/")
def get(session):
    session.setdefault("counter", 0)
    session["counter"] = session.get("counter") + 1
    counter = session["counter"]

    return Div(P(f"Hello World -- {counter}"), hx_get="/change")


@rt("/change")
def get():
    return P("Nice to be here!")
