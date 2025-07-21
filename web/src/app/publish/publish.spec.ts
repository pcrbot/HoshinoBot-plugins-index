import { ComponentFixture, TestBed } from '@angular/core/testing';

import { Publish } from './publish';

describe('Publish', () => {
  let component: Publish;
  let fixture: ComponentFixture<Publish>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [Publish]
    })
    .compileComponents();

    fixture = TestBed.createComponent(Publish);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
