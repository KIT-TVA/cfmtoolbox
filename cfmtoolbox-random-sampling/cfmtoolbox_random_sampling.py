from cfmtoolbox import app


@app.command()
def random_sampling(rate: float = 0.5):
    print("Sampling Randomly at rate", rate)
