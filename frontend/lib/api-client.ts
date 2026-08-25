import { config, API_ENDPOINTS } from "./config";
import { FetchPlayersParams, PlayerStats, PlayerResponse, Badge, PlayerMove, SimilarPlayer, RadarData, EvolutionData } from "@/types";

type YearParam = number | null | "career";

class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = config.apiUrl) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;

    const defaultHeaders = {
      "Content-Type": "application/json",
    };

    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...defaultHeaders,
          ...options.headers,
        },
      });

      if (!response.ok) {
        const errorText = await response.text();
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof Error) {
        throw new Error(`Network Error: ${error.message}`);
      }
      throw new Error("Unknown network error occurred");
    }
  }

  async getPlayer(id: string, year?: YearParam): Promise<PlayerResponse> {
    const url = new URL(API_ENDPOINTS.player(id), this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<PlayerResponse>(url.pathname + url.search);
  }

  async getAllPlayers(params: FetchPlayersParams = {}): Promise<PlayerStats> {
    const {
      limit = 50,
      offset = 0,
      sort = "adj_rapm_margin",
      order = "desc",
      year,
      search,
      dataTier,
      d1Only,
      highMajorOnly,
      conf,
    } = params;

    const url = new URL(API_ENDPOINTS.players, this.baseUrl);

    url.searchParams.append("limit", String(limit));
    url.searchParams.append("offset", String(offset));
    url.searchParams.append("sort", sort);
    url.searchParams.append("order", order);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    if (search && search.trim()) {
      url.searchParams.append("search", search.trim());
    }

    if (dataTier) {
      url.searchParams.append("dataTier", dataTier);
    }

    if (d1Only) {
      url.searchParams.append("d1Only", "true");
    }

    if (highMajorOnly) {
      url.searchParams.append("highMajorOnly", "true");
    }

    if (conf) {
      url.searchParams.append("conf", conf);
    }

    return this.request<PlayerStats>(url.pathname + url.search);
  }

  async getPlayerMoves(id: string, year?: YearParam): Promise<PlayerMove[]> {
    const url = new URL(API_ENDPOINTS.playerMoves(id), this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<PlayerMove[]>(url.pathname + url.search);
  }

  async getPlayerBadges(id: string, year?: YearParam): Promise<Badge[]> {
    const url = new URL(API_ENDPOINTS.playerBadges(id), this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<Badge[]>(url.pathname + url.search);
  }

  async getSimilarPlayers(
    id: string,
    styleWeight = 0.7,
    year?: YearParam
  ): Promise<SimilarPlayer[]> {
    const url = new URL(API_ENDPOINTS.playerSimilar(id), this.baseUrl);

    url.searchParams.append("style_weight", String(styleWeight));

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<SimilarPlayer[]>(url.pathname + url.search);
  }

  async getPlayerRadar(id: string, year?: YearParam): Promise<RadarData> {
    const url = new URL(API_ENDPOINTS.playerRadar(id), this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<RadarData>(url.pathname + url.search);
  }

  async getPlayerEvolution(id: string, year?: YearParam): Promise<EvolutionData> {
    const url = new URL(API_ENDPOINTS.playerEvolution(id), this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<EvolutionData>(url.pathname + url.search);
  }

  async getYears(): Promise<number[]> {
    return this.request<number[]>(API_ENDPOINTS.years);
  }

  async getMovesRankings(moveType: string, year?: YearParam, limit: number = 50, offset: number = 0, position?: string, conference?: string, highMajor?: boolean, search?: string, sortBy?: string, sortOrder?: "asc" | "desc"): Promise<any> {
    const url = new URL(API_ENDPOINTS.movesRankings, this.baseUrl);

    url.searchParams.append("move_type", moveType);
    url.searchParams.append("limit", String(limit));
    url.searchParams.append("offset", String(offset));

    if (year !== undefined && year !== null && year !== "career") {
      url.searchParams.append("year", String(year));
    }

    if (position !== undefined && position !== null && position !== "all") {
      url.searchParams.append("position", position);
    }

    if (conference !== undefined && conference !== null && conference !== "all") {
      url.searchParams.append("conference", conference);
    }

    if (highMajor !== undefined && highMajor !== null) {
      url.searchParams.append("high_major", String(highMajor));
    }

    if (search && search.trim()) {
      url.searchParams.append("search", search.trim());
    }

    if (sortBy !== undefined && sortBy !== null) {
      url.searchParams.append("sort_by", sortBy);
    }

    if (sortOrder !== undefined && sortOrder !== null) {
      url.searchParams.append("sort_order", sortOrder);
    }

    return this.request<any>(url.pathname + url.search);
  }

  async getAllTeams(year?: YearParam): Promise<any> {
    const url = new URL(API_ENDPOINTS.teams, this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<any>(url.pathname + url.search);
  }

  async getTeam(id: string, year?: YearParam): Promise<any> {
    const url = new URL(API_ENDPOINTS.team(id), this.baseUrl);

    if (year !== undefined && year !== null) {
      url.searchParams.append("year", String(year));
    }

    return this.request<any>(url.pathname + url.search);
  }
}

export const apiClient = new ApiClient();

export const fetchPlayer = apiClient.getPlayer.bind(apiClient);
export const fetchAllPlayers = apiClient.getAllPlayers.bind(apiClient);
export const fetchPlayerMoves = apiClient.getPlayerMoves.bind(apiClient);
export const fetchPlayerBadges = apiClient.getPlayerBadges.bind(apiClient);
export const fetchSimilarPlayers = apiClient.getSimilarPlayers.bind(apiClient);
export const fetchPlayerRadar = apiClient.getPlayerRadar.bind(apiClient);
export const fetchPlayerEvolution = apiClient.getPlayerEvolution.bind(apiClient);
export const fetchTeam = apiClient.getTeam.bind(apiClient);
export const fetchAllTeams = apiClient.getAllTeams.bind(apiClient);
