// Copyright (c) 2017 Computer Vision Center (CVC) at the Universitat Autonoma de Barcelona (UAB). This work is licensed under the terms of the MIT license. For a copy, see <https://opensource.org/licenses/MIT>.


#include "DebrisGenerationWidget.h"

#define DEBUG_MSG(x, ...) if(GEngine){GEngine->AddOnScreenDebugMessage(-1, 15.0f, FColor::Red, FString::Printf(TEXT(x), __VA_ARGS__));}

UDebrisGenerationWidget::UDebrisGenerationWidget()
{
}

UDebrisGenerationWidget::~UDebrisGenerationWidget()
{
}

void UDebrisGenerationWidget::Hello()
{
	DEBUG_MSG("Hello")
}

void UDebrisGenerationWidget::GenerateDebris()
{
	DEBUG_MSG("Generate Debris")
}

void UDebrisGenerationWidget::ClearDebris()
{
	DEBUG_MSG("Clear Debris")
}