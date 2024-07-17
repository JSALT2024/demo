import { Connection } from "./connection/Connection";
import { Video } from "./model/Video";

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
      `videos/${id}/reprocess`
    );

    if (response.status !== 202) {
      throw response;
    }
  }
}
