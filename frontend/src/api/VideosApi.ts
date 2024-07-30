import { Connection } from "./connection/Connection";
import { ClipsCollection } from "./model/ClipsCollection";
import { FrameGeometry } from "./model/FrameGeometry";
import { Video } from "./model/Video";
import { VideoCrops } from "./model/VideoCrops";

export interface RetranslateRequest {
  use_mae: boolean;
  use_dino: boolean;
  use_sign2vec: boolean;
  prompt: string;
}

export interface LogFollower {
  readonly close: () => void;
  readonly startFollowing: () => Promise<void>;
}

export class VideosApi {
  private connection: Connection;

  constructor(connection: Connection) {
    this.connection = connection;
  }

  async list(): Promise<Video[]> {
    const response = await this.connection.request("GET", "videos");
    if (response.status !== 200) {
      throw response;
    }
    return (await response.json()) as Video[];
  }

  async get(id: string): Promise<Video> {
    const response = await this.connection.request("GET", "videos/" + id);
    if (response.status !== 200) {
      throw response;
    }
    return (await response.json()) as Video;
  }

  getUploadedVideoFileUrl(id: string): URL {
    return this.connection.url(`videos/${id}/uploaded-file`);
  }

  getNormalizedVideoFileUrl(id: string): URL {
    return this.connection.url(`videos/${id}/normalized-file`);
  }

  getCropsUrl(id: string, cropName: string): URL {
    return this.connection.url(`videos/${id}/cropped/${cropName}`);
  }

  followLog(id: string, handleLine: (line: string) => void): LogFollower {
    const connection = this.connection;
    const abortController = new AbortController();
    let response: Response | null = null;
    let closed = false;

    return {
      async startFollowing() {
        response = await connection.request(
          "GET",
          `videos/${id}/log`,
          { signal: abortController.signal }
        );
        if (response === null) return;
        if (response.status !== 200) throw response;
        if (response.body === null) return;
        
        const textReader = response.body
          .pipeThrough(new TextDecoderStream())
          .getReader();

        try {
          while (true) {
            const { done, value } = await textReader.read();
            if (done) break;
            handleLine(value);
          }
        } catch (e) {
          // when the request is aborted an exception is thrown
          // that's ok!
          if (!closed) throw e;
        }
      },
      close() {
        closed = true;
        abortController.abort();
      }
    };
  }

  async getNormalizedVideoBlob(id: string): Promise<Blob | null> {
    const response = await this.connection.request(
      "GET",
      `videos/${id}/normalized-file`,
    );
    if (response.status === 404) {
      return null;
    }
    if (response.status !== 200) {
      throw response;
    }
    return await response.blob();
  }

  async getFrameGeometries(id: string): Promise<FrameGeometry[] | null> {
    const response = await this.connection.request(
      "GET",
      `videos/${id}/geometry`,
    );
    if (response.status === 404) {
      return null;
    }
    if (response.status !== 200) {
      throw response;
    }
    return (await response.json()) as FrameGeometry[];
  }

  async getClipsCollection(id: string): Promise<ClipsCollection | null> {
    const response = await this.connection.request(
      "GET",
      `videos/${id}/clips-collection`,
    );
    if (response.status === 404) {
      return null;
    }
    if (response.status !== 200) {
      throw response;
    }
    return (await response.json()) as ClipsCollection;
  }

  async getCropFrames(id: string, cropName: string): Promise<Blob[] | null> {
    const response = await this.connection.request(
      "GET",
      `videos/${id}/cropped/${cropName}`,
    );
    if (response.status === 404) {
      return null;
    }
    if (response.status !== 200) {
      throw response;
    }
    const json = await response.json();

    const blobs: Blob[] = [];
    for (const base64Text of json) {
      const binary = atob(base64Text);
      var array = new Uint8Array(binary.length);
      for (let i = 0; i < binary.length; i++) {
        array[i] = binary.charCodeAt(i);
      }
      const blob = new Blob([array], { type: "image/jpeg" });
      blobs.push(blob);
    }

    return blobs;
  }

  async getCrops(id: string): Promise<VideoCrops | null> {
    const data = {
      right_hand: await this.getCropFrames(id, "right_hand"),
      left_hand: await this.getCropFrames(id, "left_hand"),
      face: await this.getCropFrames(id, "face"),
      images: await this.getCropFrames(id, "images"),
    };
    if (data.right_hand === null) return null;
    if (data.left_hand === null) return null;
    if (data.face === null) return null;
    if (data.images === null) return null;
    return data as VideoCrops;
  }

  async upload(
    videoBlob: Blob,
    videoTitle: string,
    mediaType: string,
  ): Promise<void> {
    const body = new FormData();
    body.append(
      "media_type", // parameter name
      mediaType, // parameter value
    );
    body.append(
      "file", // parameter name
      videoBlob, // video binary data
      videoTitle, // file name
    );

    const response = await this.connection.request("POST", "videos", { body });

    if (response.status !== 201) {
      throw response;
    }
  }

  async reprocess(id: string): Promise<void> {
    const response = await this.connection.request(
      "POST",
      `videos/${id}/reprocess`,
    );

    if (response.status !== 202) {
      throw response;
    }
  }

  async retranslate(
    videoId: string,
    clipIndex: number,
    body: RetranslateRequest,
  ): Promise<string> {
    const response = await this.connection.request(
      "POST",
      `videos/${videoId}/clip/${clipIndex}/retranslate`,
      { body },
    );

    if (response.status !== 200) {
      throw response;
    }

    const data = await response.json();
    return data.llm_response as string;
  }
}
