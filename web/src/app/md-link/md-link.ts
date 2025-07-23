import { Component, input, OnInit, signal } from "@angular/core";
import { CommonModule } from "@angular/common";

// 定义节点类型
interface TextNode {
  type: "text" | "link";
  content: string;
  url?: string;
}

@Component({
  selector: "app-md-link",
  standalone: true,
  imports: [CommonModule],
  templateUrl: "./md-link.html",
  styleUrl: "./md-link.scss",
})
export class MdLink implements OnInit {
  mdContent = input.required<string>();
  textNodes = signal<TextNode[]>([]);

  ngOnInit() {
    this.parseMarkdown();
  }

  parseMarkdown() {
    const input = this.mdContent() || "";
    const nodes: TextNode[] = [];

    // 使用正则表达式匹配Markdown链接
    const linkPattern = /\[([^\]]+)\]\(([^)]+)\)/g;

    let lastIndex = 0;
    let match;

    // 遍历所有匹配的链接
    while ((match = linkPattern.exec(input)) !== null) {
      // 如果链接前有文本，添加为文本节点
      if (match.index > lastIndex) {
        nodes.push({
          type: "text",
          content: input.substring(lastIndex, match.index),
        });
      }

      // 添加链接节点
      nodes.push({
        type: "link",
        content: match[1], // 链接文本
        url: match[2], // 链接URL
      });

      lastIndex = match.index + match[0].length;
    }

    // 添加剩余的文本
    if (lastIndex < input.length) {
      nodes.push({
        type: "text",
        content: input.substring(lastIndex),
      });
    }

    // 将结果设置到signal中
    this.textNodes.set(nodes);
  }
}
