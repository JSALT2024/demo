import { Connection } from "./connection/Connection";
import { FrameGeometry } from "./model/FrameGeometry";
import { Video } from "./model/Video";
import { VideoCrops } from "./model/VideoCrops";

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

  async getFrameGeometries(id: string): Promise<FrameGeometry[]> {
    const response = await this.connection.request(
      "GET",
      `videos/${id}/geometry`
    );
    if (response.status !== 200) {
      throw response;
    }
    return (await response.json()) as FrameGeometry[];
  }

  async getCropFrames(id: string, cropName: string): Promise<Blob[]> {
    const response = await this.connection.request(
      "GET",
      `videos/${id}/cropped/${cropName}`
    );
    if (response.status !== 200) {
      throw response;
    }
    const json = await response.json();

    const blobs: Blob[] = [];
    for (const base64Text of json) {
      const binary = atob(base64Text);
      var array = new Uint8Array(binary.length)
      for (let i = 0; i < binary.length; i++) {
        array[i] = binary.charCodeAt(i);
      }
      const blob = new Blob([array], {type: "image/jpeg"});
      blobs.push(blob);
    }

    return blobs;
  }

  async getCrops(id: string): Promise<VideoCrops> {
    return {
      face: await this.getCropFrames(id, "face")
    }
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
