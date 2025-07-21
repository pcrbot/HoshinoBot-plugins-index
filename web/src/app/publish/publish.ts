import { Component, inject } from "@angular/core";
import {
  FormArray,
  FormBuilder,
  ReactiveFormsModule,
  Validators,
} from "@angular/forms";
import { MatButtonModule } from "@angular/material/button";
import {
  MatDialogActions,
  MatDialogClose,
  MatDialogContent,
  MatDialogTitle,
} from "@angular/material/dialog";
import { MatFormFieldModule } from "@angular/material/form-field";
import { MatIconModule } from "@angular/material/icon";
import { MatInputModule } from "@angular/material/input";

@Component({
  selector: "app-publish",
  imports: [
    ReactiveFormsModule,
    MatDialogTitle,
    MatDialogContent,
    MatDialogActions,
    MatDialogClose,
    MatButtonModule,
    MatFormFieldModule,
    MatInputModule,
    MatIconModule,
  ],
  templateUrl: "./publish.html",
  styleUrl: "./publish.scss",
})
export class Publish {
  private formBuilder = inject(FormBuilder);

  form = this.formBuilder.group({
    name: ["", Validators.required],
    link: ["", Validators.required],
    description: [""],
    authors: this.formBuilder.array([
      this.formBuilder.group({
        name: ["", Validators.required],
        link: ["", Validators.required],
      }),
    ]),
    comment: [""],
  });
  public get authors(): FormArray {
    return this.form.get("authors") as FormArray;
  }
  addAuthor() {
    this.authors.push(
      this.formBuilder.group({
        name: ["", Validators.required],
        link: ["", Validators.required],
      })
    );
  }
  removeLastAuthor() {
    if (this.authors.length > 1) {
      this.authors.removeAt(this.authors.length - 1);
    }
  }
  confirmClicked() {
    if (!this.form.valid) {
      return;
    }
    const toml = this.generatePluginToml();
    const body = this.form.value.comment + "\n```toml\n" + toml + "\n```";
    this.openLink(
      "https://github.com/pcrbot/HoshinoBot-plugins-index/issues/new",
      { title: "发布插件：" + this.form.value.name, labels: "publish", body }
    );
  }

  private generatePluginToml() {
    const { name, link, description, authors } = this.form.value;

    const authorStr = authors
      ?.map(
        (author) => `[[authors]]
name = ${JSON.stringify(author.name)}
link = ${JSON.stringify(author.link)}`
      )
      .join("\n");

    return `name = ${JSON.stringify(name)}
link = ${JSON.stringify(link)}
description = ${JSON.stringify(description)}
${authorStr}`;
  }

  private openLink(link: string, params: Record<string, string> = {}) {
    const queryString = new URLSearchParams(params).toString();
    if (queryString) {
      link += `?${queryString}`;
    }
    window.open(link, "_blank", "noopener,noreferrer");
  }
}
