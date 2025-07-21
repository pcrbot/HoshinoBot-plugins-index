import { Pipe, PipeTransform } from "@angular/core";

async function sha256Hex(str: string): Promise<string> {
  const buffer = new TextEncoder().encode(str);
  const hash = await crypto.subtle.digest("SHA-256", buffer);
  return Array.from(new Uint8Array(hash))
    .map((b) => b.toString(16).padStart(2, "0"))
    .join("");
}

@Pipe({
  name: "editLink",
})
export class EditLinkPipe implements PipeTransform {
  async transform(pluginLink: string): Promise<string> {
    const githubPattern =
      /^https:\/\/github\.com\/([^\/]+)\/([^\/]+)(\/?(?:tree|blob)\/(?:.+))?$/;
    let match = pluginLink.match(githubPattern);
    if (match) {
      const user = encodeURIComponent(match[1]);
      const repo = encodeURIComponent(match[2]);
      const path = match[3];
      if (path) {
        const linkHash = await sha256Hex(pluginLink);
        return `https://github.com/pcrbot/HoshinoBot-plugins-index/edit/master/plugins/${user}/${repo}/${linkHash}.json`;
      } else {
        return `https://github.com/pcrbot/HoshinoBot-plugins-index/edit/master/plugins/${user}/${repo}.json`;
      }
    }

    const linkHash = await sha256Hex(pluginLink);
    return `https://github.com/pcrbot/HoshinoBot-plugins-index/tree/master/plugins/others/${linkHash}.json`;
  }
}
