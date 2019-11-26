import argparse

import torch
import torch.nn as nn
from torchvision import transforms

from data_loader import get_loader
from model import ClassificationCNN


def train(args):
    # Image preprocessing, normalization for the pretrained resnet
    transform = transforms.Compose([
        transforms.ToTensor(),
        transforms.Normalize((0.485, 0.456, 0.406),
                             (0.229, 0.224, 0.225))
    ])

    # Build data loader
    data_loader = get_loader(
        args.image_dir, transform, args.batch_size, shuffle=True, num_workers=args.num_workers
    )

    # Device configuration
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    print('training on', device)

    # Build the models
    model = ClassificationCNN().to(device)

    # Loss and optimizer
    criterion = nn.BCELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=args.learning_rate)

    # Train the models
    total_step = len(data_loader)
    for epoch in range(args.num_epochs):
        for i, (images, targets) in enumerate(data_loader):

            # Set mini-batch dataset
            images = images.to(device)

            # Forward, backward and optimize
            outputs = model(images)
            loss = criterion(outputs, targets)
            model.zero_grad()
            loss.backward()
            optimizer.step()

            # Print log info
            if i % args.log_step == 0:
                log_info = 'Epoch [{}/{}], Step [{}/{}], Loss: {:.4f}'.format(
                    epoch, args.num_epochs, i, total_step, loss.item()
                )
                print(log_info)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--model_path', type=str, default='models/', help='path for saving trained models')
    parser.add_argument('--image_dir', type=str, default='../dataset/images_tiny', help='directory for input images')
    parser.add_argument('--log_step', type=int, default=10, help='step size for printing log info')
    parser.add_argument('--save_step', type=int, default=1000, help='step size for saving trained models')

    parser.add_argument('--num_epochs', type=int, default=5)
    parser.add_argument('--batch_size', type=int, default=128)
    parser.add_argument('--num_workers', type=int, default=2)
    parser.add_argument('--learning_rate', type=float, default=0.001)
    args = parser.parse_args()
    train(args)


if __name__ == '__main__':
    main()
