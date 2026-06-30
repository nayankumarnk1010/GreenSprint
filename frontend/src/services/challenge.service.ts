import { API_BASE_URL } from "@/lib/api";
import { AuthService } from "./auth.service";

import type {
  Challenge,
  ChallengeParticipant,
} from "@/types/challenge";

export class ChallengeService {
  static async getChallenges(): Promise<Challenge[]> {
    const token = AuthService.getToken();

    const response = await fetch(
      `${API_BASE_URL}/challenges`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        "Failed to load challenges"
      );
    }

    return response.json();
  }

  static async getMyChallenges(): Promise<
    ChallengeParticipant[]
  > {
    const token = AuthService.getToken();

    const response = await fetch(
      `${API_BASE_URL}/challenges/my`,
      {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      }
    );

    if (!response.ok) {
      throw new Error(
        "Failed to load challenges"
      );
    }

    return response.json();
  }

  static async generateChallenge(
    goal: string
  ): Promise<Challenge> {
    const token = AuthService.getToken();

    const response = await fetch(
      `${API_BASE_URL}/challenges/generate`,
      {
        method: "POST",
        headers: {
          "Content-Type":
            "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          goal,
        }),
      }
    );

    if (!response.ok) {
      const error =
        await response.text();

      console.error(
        "Generate Challenge Error:",
        error
      );

      throw new Error(
        "Failed to generate challenge"
      );
    }

    return response.json();
  }

  static async joinChallenge(
    challengeId: string
  ) {
    const token = AuthService.getToken();

    const response = await fetch(
      `${API_BASE_URL}/challenges/${challengeId}/join`,
      {
        method: "POST",
        headers: {
          Authorization: `Bearer ${token}`,
          "Content-Type":
            "application/json",
        },
      }
    );

    if (!response.ok) {
      const error =
        await response.text();

      console.error(
        "Join Challenge Error:",
        error
      );

      throw new Error(error);
    }

    return response.json();
  }

  static async updateProgress(
    challengeId: string,
    progress: number
  ) {
    const token = AuthService.getToken();

    const response = await fetch(
      `${API_BASE_URL}/challenges/${challengeId}/progress`,
      {
        method: "PATCH",
        headers: {
          "Content-Type":
            "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          progress,
        }),
      }
    );

    if (!response.ok) {
      const error =
        await response.text();

      console.error(
        "Update Progress Error:",
        error
      );

      throw new Error(
        "Failed to update progress"
      );
    }

    return response.json();
  }
}