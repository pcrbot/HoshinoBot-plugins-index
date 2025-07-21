import { AsyncPipe, DatePipe } from "@angular/common";
import { HttpClient } from "@angular/common/http";
import { Component, computed, inject, OnInit, signal } from "@angular/core";
import { MatTableModule } from "@angular/material/table";
import { MdLink } from "./md-link/md-link";
import { MatButtonModule } from "@angular/material/button";
import { MatToolbarModule } from "@angular/material/toolbar";
import { MatIconModule, MatIconRegistry } from "@angular/material/icon";
import { DomSanitizer } from "@angular/platform-browser";
import { EditLinkPipe } from "./edit-link-pipe";

type Plugin = {
  name: string;
  link: string;
  description?: string;
  authors: { name: string; link: string }[];
  last_updated?: number; // unix timestamp
  stars?: number;
};

@Component({
  selector: "app-root",
  imports: [
    MatIconModule,
    MatToolbarModule,
    MatButtonModule,
    MatTableModule,
    DatePipe,
    AsyncPipe,
    MdLink,
    EditLinkPipe,
  ],
  templateUrl: "./app.html",
  styleUrl: "./app.scss",
})
export class App implements OnInit {
  httpClient = inject(HttpClient);
  plugins = signal<Plugin[]>([]);
  orderBy = signal<keyof Plugin>("last_updated");
  reverseOrder = signal(false);
  editMode = signal(false);

  displayedPlugins = computed(() => {
    const orderBy = this.orderBy();
    const plugins = [...this.plugins()];
    plugins.sort((a, b) => {
      if (a[orderBy] == null) return 1;
      if (b[orderBy] == null) return -1;
      if (a[orderBy]! < b[orderBy]!) return 1;
      if (a[orderBy]! > b[orderBy]!) return -1;
      return 0;
    });
    if (this.reverseOrder()) {
      plugins.reverse();
    }
    return plugins;
  });

  displayedColumns = computed(() =>
    this.editMode()
      ? ["title", "authors", "edit"]
      : ["title", "stars", "description", "authors", "last_updated"]
  );

  constructor() {
    this.setupSvgIcons();
  }

  ngOnInit() {
    this.fetchPlugins();
  }

  private setupSvgIcons() {
    const iconRegistry = inject(MatIconRegistry);
    const sanitizer = inject(DomSanitizer);
    iconRegistry.addSvgIcon(
      "github",
      sanitizer.bypassSecurityTrustResourceUrl("github-mark.svg"),
      { viewBox: "0 0 98 96" }
    );
  }

  private fetchPlugins() {
    this.httpClient.get<Plugin[]>("/plugins.json").subscribe((data) => {
      this.plugins.set(data);
    });
  }

  sortClicked(column: keyof Plugin) {
    if (this.orderBy() === column) {
      this.reverseOrder.set(!this.reverseOrder());
    } else {
      this.orderBy.set(column);
      this.reverseOrder.set(false);
    }
  }

  editClicked() {
    this.editMode.set(!this.editMode());
  }
}
