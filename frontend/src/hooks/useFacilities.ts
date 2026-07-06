import { useQuery } from "@tanstack/react-query";
import { facilitiesAPI } from "../services/api";

export function useFacilities() {
  return useQuery({
    queryKey: ["facilities"],

    queryFn: async () => {
      const response = await facilitiesAPI.getAll();
      return response.data;
    },
  });
}