from api.constants import API_PAGINATION
from django.core.paginator import Paginator

def GetPagesData(page,data):
    if page:
        if str(page) == "1":
            start = 0
            end = start + API_PAGINATION
        else:
            start = API_PAGINATION * (int(page)-1)
    else:
        start = 0
        end =start + API_PAGINATION
    page_data_value = Paginator(data,API_PAGINATION)
    last_page = True if page_data_value.num_pages == int(page if page else 1) else False
    meta_data = {
        "page_count":page_data_value.num_pages,
        "total_results":data.count(),
        "current_page_no":int(page if page else 1),
        "limit":API_PAGINATION,
        "last_page":last_page,
    }
    return start,end,meta_data