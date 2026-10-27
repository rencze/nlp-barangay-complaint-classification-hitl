"""Small executable classification demonstration; not a thesis evaluation."""
from pathlib import Path
from train import build_pipeline, load_dataset


def main():
    data=Path(__file__).resolve().parents[1]/'examples/demo_complaints.csv'
    text,labels=load_dataset(data)
    model=build_pipeline(42).fit(text,labels)
    examples=['Sirang ilaw sa kanto at madilim ang daan.', 'Buy now! Visit our store for a discount.']
    for narrative,label in zip(examples,model.predict(examples)):
        print(f'{narrative} -> {label}')
    print('Demo only: this output is not an independent evaluation or a research score.')


if __name__=='__main__':main()
