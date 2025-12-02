import axios from "axios"
import type { Vacancy } from "../../../entities/Vacancy/types"


export const getVacancyList = async () => {
    return (await axios.get<Vacancy[]>('/')).data
}