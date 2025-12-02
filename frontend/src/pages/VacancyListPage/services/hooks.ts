import { useQuery } from "@tanstack/react-query"
import { getVacancyList } from "./api"


export const useGetVacanciesList = () => {
    return useQuery({
        queryKey:['vacanciesList'],
        queryFn: getVacancyList
    })
}