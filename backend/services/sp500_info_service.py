from repository.sp500_company_repository import SP500CompanyRepository

class SP500InfoService:
    def __init__(self, repo: SP500CompanyRepository):
        self.sp500_repo = repo

    def get_all_companies(self) -> list[dict]:
        return self.sp500_repo.get_all_companies()
    